import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


class AssistantBase:
    def reply(self, message: str) -> str:
        raise NotImplementedError()


class MockAssistant(AssistantBase):
    def reply(self, message: str) -> str:
        # simple deterministic mock
        return f"(mock) I understood: {message}"


class OpenAIAssistant(AssistantBase):
    def __init__(self, api_key: str, max_concurrent: int = 4, max_retries: int = 4):
        try:
            import openai
        except Exception:
            raise RuntimeError('openai package is required for OpenAIAssistant')
        openai.api_key = api_key
        self.openai = openai
        self.semaphore = __import__('threading').Semaphore(max_concurrent)
        # lazy import tenacity to avoid failing when it's not installed at import-time
        try:
            from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
            from tenacity import retry_if_exception  # noqa: F401
        except Exception:
            raise RuntimeError('tenacity is required for retries; please install it')

        # Define retry decorator used by reply
        def _retry_on_exceptions():
            from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

            return retry(
                reraise=True,
                stop=stop_after_attempt(max_retries),
                wait=wait_exponential(multiplier=1, min=1, max=10),
                retry=retry_if_exception_type((self.openai.error.Timeout, self.openai.error.APIError, self.openai.error.RateLimitError)),
            )

        self._retry_decorator = _retry_on_exceptions()

    def _call_api(self, message: str):
        # perform the ChatCompletion call
        return self.openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': message}],
            max_tokens=256,
            temperature=0.2,
        )

    def reply(self, message: str) -> str:
        # Acquire semaphore to limit concurrent OpenAI requests
        acquired = self.semaphore.acquire(timeout=10)
        if not acquired:
            raise RuntimeError('server busy; try again later')

        try:
            # Call API with retry/backoff
            wrapped = self._retry_decorator(self._call_api)
            resp = wrapped(message)
            choices = resp.get('choices') or []
            if choices:
                return choices[0].get('message', {}).get('content', '').strip()
            return ''
        finally:
            self.semaphore.release()


def get_assistant():
    provider = os.environ.get('ASSISTANT_PROVIDER', 'mock').lower()
    if provider == 'openai':
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise RuntimeError('OPENAI_API_KEY not set for OpenAI provider')

        # Read concurrency and retry settings from environment with sensible defaults
        try:
            max_concurrent = int(os.environ.get('MAX_CONCURRENT', '4'))
        except ValueError:
            max_concurrent = 4
        try:
            max_retries = int(os.environ.get('MAX_RETRIES', '4'))
        except ValueError:
            max_retries = 4

        return OpenAIAssistant(api_key, max_concurrent=max_concurrent, max_retries=max_retries)
    return MockAssistant()


assistant = None


def init_assistant():
    """Initialize the assistant provider. Registered to run before first request when available,
    otherwise called at import time to ensure tests and environments without that hook work.
    """
    global assistant
    try:
        assistant = get_assistant()
    except Exception as e:
        # fallback to mock but log
        print('Failed to init assistant provider:', e)
        assistant = MockAssistant()


# Register initializer if Flask supports the hook, otherwise call it now so assistant is set.
if hasattr(app, 'before_first_request'):
    try:
        app.before_first_request(init_assistant)
    except Exception:
        # as a safe fallback, call directly
        init_assistant()
else:
    init_assistant()


@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok', 'message': 'MobAI backend is running'})


@app.route('/assist', methods=['POST'])
def assist():
    data = request.json or {}
    message = data.get('message', '')

    if not message:
        return jsonify({'error': 'no message provided'}), 400

    try:
        reply_text = assistant.reply(message)
    except Exception as e:
        return jsonify({'error': f'assistant error: {e}'}), 500

    return jsonify({'reply': reply_text})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


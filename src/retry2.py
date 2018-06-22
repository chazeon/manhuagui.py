import time

def retry2(handle: callable, backoff_factor: float = 0.3, max_retry: int = 5):
    try:
        return handle()
    except Exception as err:
        print(err)
        if max_retry > 0:
            time.sleep(backoff_factor)
            return retry2(handle, backoff_factor, max_retry=max_retry - 1)
        else:
            raise err

import os


class LocalConfig:
    @staticmethod
    def load(BASE_DIR: str):
        try:
            from dotenv import load_dotenv

            env_path = os.path.join(BASE_DIR, "conf/.env")
            if os.path.isfile(env_path):
                load_dotenv(dotenv_path=env_path)
            else:
                raise Exception("Did you create your local .env configuration file?")
        except Exception as _:
            raise Exception("Did you install requirements into your local environment?")

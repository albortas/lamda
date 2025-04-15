import toml

# Variable global para almacenar la configuración cargada
_cached_config = None

def load_config(file_path):
    global _cached_config
    if _cached_config is None:
        try:
            with open(file_path, 'r') as file:
                _cached_config = toml.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"El archivo de configuración '{file_path}' no fue encontrado.")
        except toml.TomlDecodeError:
            raise ValueError(f"El archivo de configuración '{file_path}' tiene un formato incorrecto.")
    return _cached_config

def get_config(file_path='src/config/config_general.toml'):
    return load_config(file_path)
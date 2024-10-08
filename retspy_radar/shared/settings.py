from typing import Any

from ..base.exceptions import ConfigurationFileError
from ..base.settings import SettingsValue


class Settings:

    def __init__(self, settings: SettingsValue) -> None:
        self._settings: SettingsValue = self._validate_ver_1_0(settings)

    @classmethod
    def _validate_ver_1_0(cls, settings: SettingsValue) -> SettingsValue:
        """
        Valida los valores de las configuraciones.

        Raises
        ------
        ConfigurationFileError
            Si alguna configuración no es válida.
        """
        service_id: str = settings["args"]["command"].as_type(str)

        service: SettingsValue = settings[service_id]

        if service.has("client"):
            settings["client"].update(service["client"])

        if service.has("timing"):
            settings["timing"].update(service["timing"])

        try:
            preamble = f"El servicio '{service_id}' "

            assert service.has("metadata"), f"{preamble} no tiene metadatos"

            assert service["metadata"].has(
                "name"
            ), f"{preamble} no tiene nombre"

            assert service["metadata"].has(
                "description"
            ), f"{preamble} no tiene descripción"

            assert service["metadata"].has(
                "organization"
            ), f"{preamble} no tiene nombre organización"

            assert service["metadata"].has(
                "country"
            ), f"{preamble} no tiene país de origen"

            assert service["metadata"].has(
                "product"
            ), f"{preamble} no tiene información de producto"

            assert service.has(
                "server"
            ), f"{preamble} no tiene información de servidor"

            assert service["server"].has(
                "base_url"
            ), f"{preamble} no tiene la URL del sitio web"

            assert service["server"].has(
                "radar_url"
            ), f"{preamble} no tiene la URL de la página radar"

            assert service["server"].has(
                "inventory_url"
            ), f"{preamble} no tiene la URL de acceso al inventario"

            assert service["server"].has(
                "repository_url"
            ), f"{preamble} no tiene la URL del repositorio"

            assert service.has(
                "station_groups"
            ), f"{preamble} no tiene información de grupos de estaciones"

            assert service.has(
                "stations"
            ), f"{preamble} no tiene lista de estaciones"

            stations: dict[str, dict[str, Any]] = service["stations"].to_dict()

            station_groups: dict[str, list[str]] = service[
                "station_groups"
            ].to_dict()

            for station_ids in station_groups.values():
                for station_id in station_ids:
                    assert (
                        station_id in stations
                    ), f"La estación '{station_id}' no existe"

            for station_id in stations.keys():
                station_info: SettingsValue = service["stations"]

                assert station_info[station_id].has(
                    "name"
                ), f"La estación '{station_id}' no tiene nombre"

                assert station_info[station_id].has(
                    "lat"
                ), f"La estación '{station_id}' no tiene latitud"

                assert station_info[station_id].has(
                    "lon"
                ), f"La estación '{station_id}' no tiene longitud"

        except KeyError as exc:
            raise ConfigurationFileError(
                "No existe la entrada en el archivo de configuración"
            ) from exc

        except AssertionError as exc:
            raise ConfigurationFileError(
                "El archivo de configuración no es válido"
            ) from exc

        service_dict: dict[str, Any] = service.to_dict()

        service_dict["args"] = settings["args"].to_dict()
        service_dict["client"] = settings["client"].to_dict()
        service_dict["path"] = settings["path"].to_dict()
        service_dict["timing"] = settings["timing"].to_dict()

        return service

    @property
    def base_url(self) -> str:
        """
        Obtiene la URL de la página inicial del SMN.

        Returns
        -------
        str
            La URL de la página inicial del SMN.
        """
        return self._settings["server"]["base_url"].as_type(str)

    @property
    def chunk_size(self) -> int:
        """
        Obtiene el tamaño de los fragmentos de descarga.

        Returns
        -------
        int
            El tamaño de los fragmentos de descarga en bytes.
        """
        return self._settings["client"]["chunk_size"].as_type(int)

    @property
    def current_dir(self) -> str:
        """
        Obtiene la ruta del directorio actual.

        Returns
        -------
        str
            La ruta del directorio actual.
        """
        return self._settings["path"]["current_dir"].as_type(str)

    @property
    def end_time(self) -> str:
        """
        Obtiene la hora de fin de la recolección de datos.

        Returns
        -------
        str
            La hora de fin de la recolección de datos en formato ISO
            8601.
        """
        return self._settings["args"]["end_time"].as_type(str)

    @property
    def install_dir(self) -> str:
        """
        Obtiene la ruta del directorio actual.

        Returns
        -------
        str
            La ruta del directorio actual.
        """
        return self._settings["path"]["install_dir"].as_type(str)

    @property
    def inventory_url(self) -> str:
        """
        Obtiene la URL del conjunto de imágenes disponibles.

        Returns
        -------
        str
            La URL del conjunto de imágenes disponibles.
        """
        return self._settings["server"]["inventory_url"].as_type(str)

    @property
    def output_dir(self) -> str:
        """
        Obtiene la ruta del directorio de salida de las imágenes.

        Returns
        -------
        str
            La ruta del directorio de salida de las imágenes.
        """
        return self._settings["path"]["output_dir"].as_type(str)

    @property
    def radar_url(self) -> str:
        """
        Obtiene la URL de la página de imágenes de los radares del
        SINARAME.

        Returns
        -------
        str
            La URL de la página de imágenes de radar.
        """
        return self._settings["server"]["radar_url"].as_type(str)

    @property
    def repository_path(self) -> str:
        """
        Obtiene la ruta del directorio de almacenamiento local.

        Returns
        -------
        str
            La ruta del directorio de almacenamiento local de las
            imágenes.
        """
        return self._settings["client"]["repository_path"].as_type(str)

    @property
    def repository_url(self) -> str:
        """
        Obtiene la URL del repositorio de imágenes.

        Returns
        -------
        str
            La URL del repositorio de imágenes remoto.
        """
        return self._settings["server"]["repository_url"].as_type(str)

    @property
    def request_timeout(self) -> int:
        """
        Obtiene el tiempo de espera de las solicitudes HTTP.

        Returns
        -------
        int
            El tiempo de espera de las solicitudes HTTP en segundos.
        """
        # TODO:FIXME: Implementar la configuración de tiempo de espera
        # return self._settings["client"]["request_timeout"].as_type(int)
        return 30

    @property
    def scan_interval(self) -> str:
        """
        Obtiene el intervalo de tiempo de escaneo de las imágenes.

        Returns
        -------
        int
            El intervalo de tiempo de escaneo en segundos en formato ISO
            8601.
        """
        return self._settings["timing"]["scan_interval"].as_type(str)

    @property
    def scan_period(self) -> str:
        """
        Obtiene el período de escaneo de las imágenes.

        Returns
        -------
        str
            El período de escaneo de las imágenes en formato ISO 8601.
        """
        return self._settings["args"]["scan_period"].as_type(str)

    @property
    def service(self) -> str:
        """
        Obtiene el nombre o identificador del servicio a monitorear.

        Returns
        -------
        str
            El nombre o identificador del servicio a monitorear.
        """
        return self._settings["args"]["command"].as_type(str)

    @property
    def start_time(self) -> str:
        """
        Obtiene la hora de inicio de la recolección de datos.

        Returns
        -------
        str
            La hora de inicio de la recolección de datos en formato ISO
            8601.
        """
        return self._settings["args"]["start_time"].as_type(str)

    @property
    def stations(self) -> dict[str, dict[str, Any]]:
        """
        Obtiene la información de las estaciones disponibles.

        Returns
        -------
        dict[str, dict[str, Any]]
            La información de las estaciones disponibles.
        """
        return self._settings["stations"].as_raw()

    @property
    def station_groups(self) -> dict[str, list[str]]:
        """
        Obtiene la información de los grupos de estaciones disponibles.

        Returns
        -------
        dict[str, list[str]]
            La información de los grupos de estaciones disponibles.
        """
        return self._settings["station_groups"].as_raw()

    @property
    def station_ids(self) -> list[str]:
        """
        Obtiene los identificadores de las estaciones a escanear.

        Returns
        -------
        list[str]
            Los identificadores de las estaciones a escanear.
        """
        return self._settings["args"]["station_ids"].as_type(list[str])

    @property
    def verbosity(self) -> list[str]:
        """
        Obtiene el nivel de verbosidad de los mensajes.

        Returns
        -------
        list[str]
            El nivel de verbosidad de los mensajes.
        """
        return self._settings["args"]["verbosity"].as_type(list[str])

    @property
    def wait_for_next_authorization(self) -> str:
        """
        Obtiene el tiempo de espera entre solicitudes de autorización.

        Returns
        -------
        str
            El tiempo de espera entre solicitudes de autorización en
            formato ISO 8601.
        """
        return self._settings["timing"]["wait_for_next_authorization"].as_type(
            str
        )

    @property
    def wait_for_next_request(self) -> str:
        """
        Obtiene el tiempo de espera entre solicitudes HTTP.

        Returns
        -------
        str
            El tiempo de espera entre solicitudes en formato ISO 8601.
        """
        return self._settings["timing"]["wait_for_next_request"].as_type(str)

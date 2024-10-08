from datetime import datetime, timedelta
from logging import Logger
from typing import Any

from ..base.exceptions import (
    InvalidTimeFormatError,
    InvalidTimeRangeError,
    TimeConversionError,
)
from ..base.logging import get_logger
from ..base.settings import SettingsBasic
from ..base.utils import console, timing
from ..package_info import pkg_info
from ..shared import RobotBasic, Settings
from ..sinarame import RobotSMN


class Application:
    def __init__(self, settings: SettingsBasic) -> None:
        """
        Inicializa la aplicación.

        Parameters
        ----------
        settings : Settings
            Los ajustes de configuración de la aplicación.
        logger : Logger
            El registro de eventos de la aplicación.
        """
        self._logger: Logger = get_logger(pkg_info.name)
        self._settings: Settings = Settings(settings.root)

    def run(self) -> None:
        """
        Inicia la ejecución de la aplicación.
        """
        robot: RobotBasic = self._get_robot()

        # Mostrar el banner del programa

        robot.print_banner()

        # Iniciar la ejecución del bot de indexación de datos

        # Capturar las excepciones específicas y registrarlas en el
        # registro de eventos. Finalizar la ejecución del sistema
        # graciosa y ordenadamente
        # --------------------------------------------------------------

        args: dict[str, Any] = self._setup_arguments()

        self._print_summary(args)

        while True:
            try:

                robot.run(**args)

                break

            except KeyboardInterrupt as exc:
                terminate: str = console.prompt(
                    "¿Desea salir del programa?", console.YES_NO
                )

                if console.response_is(terminate, console.YES):
                    raise exc

        # --------------------------------------------------------------

        robot.print_footer()

    def _print_summary(self, args: dict[str, Any]) -> None:
        # Imprime el resumen de la ejecución del programa

        start_time: datetime = args["start_time"]
        end_time: datetime = args["end_time"]
        scan_interval: timedelta = args["scan_interval"]
        station_ids: list[str] = args["station_ids"]

        begin: str = start_time.strftime("%Y-%m-%dT%H:%M:%S%z")
        end: str = end_time.strftime("%Y-%m-%dT%H:%M:%S%z")

        print("Resumen de la ejecución")
        print("----------------------")
        print(f"  - Fecha de inicio         : {begin}")
        print(f"  - Fecha de finalización   : {end}")
        print(f"  - Intervalo de escaneo    : {scan_interval}")
        print(f"  - Estaciones a monitorear : {', '.join(station_ids)}\n")

        stations: dict[str, dict[str, Any]] = self._settings.stations

        for station_id in station_ids:
            if station_id in stations:
                station: dict[str, Any] = stations[station_id]
                print(f"Estación {station_id}: {station['name']}")
                print(f"  - Latitud  : {station['lat']:+02.14f}")
                print(f"  - Longitud : {station['lon']:+02.14f}\n")

    def _setup_arguments(self) -> dict[str, Any]:
        """
        Configura los argumentos de la aplicación.

        Configura los argumentos de la aplicación para la ejecución del
        proceso de recolección de datos.

        Returns
        -------
        dict[str, Any]
            Los argumentos de la aplicación.
        """
        # Fijar valores predeterminados para los parámetros de fecha y
        # hora si no se especificaron
        start_time: datetime
        end_time: datetime
        scan_period: timedelta

        # Obtener el tiempo de ejecución de la rutina; si no se
        # especifica se ejecutará la rutina por 24 horas

        if self._settings.scan_period:
            try:
                scan_period = timing.parse_timedelta(
                    self._settings.scan_period
                )

            except (InvalidTimeFormatError, TimeConversionError) as exc:
                raise TimeConversionError(
                    f"Error al leer el rango de tiempo: {exc}"
                ) from exc
        else:
            scan_period = timedelta(hours=24)

        # Obtener la fecha de inicio de ejecución de la rutina; si no
        # se especifica, se ejecutará la rutina desde el momento de la
        # llamada

        if self._settings.start_time:
            try:
                start_time = timing.parse_datetime(self._settings.start_time)

            except (InvalidTimeFormatError, TimeConversionError) as exc:
                raise TimeConversionError(
                    f"Error al leer la fecha inicial: {exc}"
                ) from exc
        else:
            start_time = timing.current_time()

        # Obtener la fecha de finalización de ejecución de la rutina; si
        # no se especifica se calcula sumando el tiempo de ejecución a
        # la fecha de inicio

        if self._settings.end_time:
            try:
                end_time = timing.parse_datetime(self._settings.end_time)

            except (InvalidTimeFormatError, TimeConversionError) as exc:
                raise TimeConversionError(
                    f"Error al leer la fecha final: {exc}"
                ) from exc
        else:
            end_time = start_time + scan_period

        # Validación de rango de fechas

        if start_time >= end_time:
            raise InvalidTimeRangeError(
                "La fecha de finalización debe ser posterior "
                "a la fecha de inicio"
            )

        scan_interval: timedelta = timing.parse_timedelta(
            self._settings.scan_interval
        )

        station_ids: list[str] = list()

        stations: dict[str, Any] = self._settings.stations
        groups: dict[str, list[str]] = self._settings.station_groups

        for station_id in self._settings.station_ids:
            if station_id in stations:
                station_ids.append(station_id)
            elif station_id in groups:
                station_ids.extend(groups[station_id])
            else:
                station_ids.append(station_id)
                self._logger.warning(
                    f"La estación '{station_id}' no está definida en la "
                    "configuración de la aplicación."
                )

        return {
            "start_time": start_time,
            "end_time": end_time,
            "scan_interval": scan_interval,
            "station_ids": station_ids,
        }

    def _get_robot(self) -> RobotBasic:
        """
        Retorna el robot de la aplicación.

        Returns
        -------
        RobotBasic
            El robot de la aplicación.

        Raises
        ------
        ValueError
            Si el servicio especificado no está soportado.
        """
        robots: list[type[RobotBasic]] = [RobotSMN]

        for robot in robots:
            if self._settings.service == robot.command:
                return robot(self._settings, self._logger)

        raise ValueError("El servicio especificado no está soportado.")

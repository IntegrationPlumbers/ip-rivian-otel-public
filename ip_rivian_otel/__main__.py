import os
import sys
import time
import importlib.util
spec = importlib.util.spec_from_file_location("Rivian", "./ip_rivian_otel/rivian-python-api/src/rivian_python_api/__init__.py")
if spec:
    mymodule = importlib.util.module_from_spec(spec)
    sys.modules['Rivian'] = mymodule
    spec.loader.exec_module(mymodule)


from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

class IPRivianOTLP:
    """
    Example OpenTelemetry collector to demonstrate sending Rivian data to Prometheus
    using OTLP.
    """

    def __init__(self, endpoint="localhost:4317"):
        self.metric_exporter = False
        self.reader = False
        self.meter_provider = False

        os.environ['OTEL_EXPORTER_OTLP_METRICS_ENDPOINT'] = endpoint
        self.resource = Resource.create(
            attributes={
                SERVICE_NAME: "ip-rivial-otel"
            }
        )

        self.rivian = mymodule.Rivian()
        self.configure_meters(endpoint)

    def configure_meters(self, endpoint):
        self.metric_exporter = OTLPMetricExporter(
            endpoint
        )

        self.reader = PeriodicExportingMetricReader(
            self.metric_exporter,
            export_interval_millis=5000
        )

        self.meter_provider = MeterProvider(
            resource=self.resource,
            metric_readers=[self.reader]
        )

        metrics.set_meter_provider(
            self.meter_provider
        )

    def get_meter(self, name=''):
        if not name == '':
            name = __name__

        meter = metrics.get_meter(name)
        return meter

    def rivian_get_vehicles(self):
        try:
            vehicles = []
            owner = self.rivian.get_user_information()
            for v in owner['data']['currentUser']['vehicles']:
                vehicles.append({
                    'id': v['id'],
                    'vin': v['vin'],
                    'model': v['vehicle']['model'],
                    'year': v['vehicle']['modelYear'],
                    'state': self.rivian_get_vehicle_state(v['id']),
                    'live_charge': self.rivian_get_live_charging_state(v['id'])
                    })
            return vehicles
        except Exception as e:
            return []

    def rivian_get_vehicle_state(self, vehicle_id):
        try:
            vs_json = self.rivian.get_vehicle_state(vehicle_id=None, minimal=False)
            if 'data' in vs_json and 'vehicleState' in vs_json['data']:
                return vs_json['data']['vehicleState']
            else:
                return []
        except Exception as e:
            return []

    def rivian_get_live_charging_state(self, vehicle_id):
        try:
            vs_json = self.rivian.get_live_session_data(vehicle_id)
            if 'data' in vs_json and 'getLiveSessionData' in vs_json['data']:
                return vs_json['data']['getLiveSessionData']
            else:
                return []
        except Exception as e:
            return []

    def rivian_get_charger_sessions(self):
        resp = self.rivian.get_completed_session_summaries()
        sessions = []
        for s in resp['data']['getCompletedSessionSummaries']:
            sessions.append({
            'charge_start': s['startInstant'],
            'charge_end': s['endInstant'],
            'energy': s['totalEnergyKwh'],
            'vendor': s['vendor'],
            'range_added': s['rangeAddedKm'],
            'transaction_id': s['transactionId'],
            })
        # sort sessions by charge_start
        sessions.sort(key=lambda x: x['charge_start'])
        return sessions

    def collect(self,sleep=90):
        active_meter = self.get_meter("Rivian")

        # Left Front
        tire_gauge_lf_good = active_meter.create_gauge(
            "riv_lf_tire_status_good",
            description="Left Front Tire OK",
            unit="1"
            )
        tire_gauge_lf_bad = active_meter.create_gauge(
            "riv_lf_tire_status_bad",
            description="Left Front Tire LOW",
            unit="1"
            )
        # Right Front
        tire_gauge_rf_good = active_meter.create_gauge(
            "riv_rf_tire_status_good",
            description="Right Front Tire OK",
            unit="1"
            )
        tire_gauge_rf_bad = active_meter.create_gauge(
            "riv_rf_tire_status_bad",
            description="Right Front Tire LOW",
            unit="1"
            )
                # Left Rear
        tire_gauge_lr_good = active_meter.create_gauge(
            "riv_lr_tire_status_good",
            description="Left Rear Tire OK",
            unit="1"
            )
        tire_gauge_lr_bad = active_meter.create_gauge(
            "riv_lr_tire_status_bad",
            description="Left Rear Tire LOW",
            unit="1"
            )
        # Right Rear
        tire_gauge_rr_good = active_meter.create_gauge(
            "riv_rr_tire_status_good",
            description="Right Rear Tire OK",
            unit="1"
            )
        tire_gauge_rr_bad = active_meter.create_gauge(
            "riv_rr_tire_status_bad",
            description="Right Rear Tire LOW",
            unit="1"
            )
        # Battery Level
        batt_level_gauge = active_meter.create_gauge(
            "riv_battery_level",
            unit="1"
        )
        # Battery Percentage
        batt_perc_gauge = active_meter.create_gauge(
            "riv_battery_percentage",
            unit="1"
        )
        # Charger State
        charg_state_gauge = active_meter.create_gauge(
            "riv_charger_state",
            unit="1",
            description="0 / 1 if the car is charging"
        )

        try:
            while True:
                v = self.rivian_get_vehicles()[0]
                charge_sessions = self.rivian_get_charger_sessions()

                vehicle_id 	= v['id']
                model 			= v['model']
                tire_lf			= 1 if v['state']['tirePressureStatusFrontLeft']['value']		== "OK" else 0
                tire_rf			= 1 if v['state']['tirePressureStatusFrontRight']['value']	== "OK" else 0
                tire_lr			= 1 if v['state']['tirePressureStatusRearLeft']['value']		== "OK" else 0
                tire_rr			= 1 if v['state']['tirePressureStatusRearRight']['value']		== "OK" else 0
                batt_level	    = v['state']['batteryLevel']['value']
                batt_cap		= v['state']['batteryCapacity']['value']
                batt_perc		= round(( batt_level / batt_cap ) * 100)
                chrg_stat 	    = 0 if v['state']['chargerStatus']['value'] == 'chrgr_sts_not_connected' else 1
                timestamp 	    = v['state']['gnssLocation']['timeStamp']

                print(f"{vehicle_id} {model} {tire_lf} {tire_rf} {tire_lr} {tire_rr} {batt_level} {batt_cap} {batt_perc} {chrg_stat} {timestamp}")

                if tire_lf == 1:
                    tire_gauge_lf_good.set(1)
                else:
                    tire_gauge_lf_bad.set(1)

                if tire_rf == 1:
                    tire_gauge_rf_good.set(1)
                else:
                    tire_gauge_rf_bad.set(1)

                if tire_lr == 1:
                    tire_gauge_lr_good.set(1)
                else:
                    tire_gauge_lr_bad.set(1)

                if tire_rr == 1:
                    tire_gauge_rr_good.set(1)
                else:
                    tire_gauge_rr_bad.set(1)

                batt_level_gauge.set(batt_level)
                batt_perc_gauge.set(batt_perc)

                charg_state_gauge.set(chrg_stat)

                time.sleep(sleep)
        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            self.meter_provider.shutdown()

def main():
    """
    Main loop for the Integration Plumbers Rivian to OTLP Collector
    Collects:
    - Live Charging Session Info
    - Last Charge Session Info
    - Battery Now
    - Tire Pressure Status
    - Vehicle Heartbeat: last seen
    """
    endpoint = "http://prometheus.ip:9090//api/v1/otlp/v1/metrics"

    otlp_service = IPRivianOTLP(endpoint=endpoint)
    otlp_service.collect(90)

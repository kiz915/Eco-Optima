import sys
sys.path.insert(0, '.')
from services.storage import init_storage, get_facility_data
from seed import seed

init_storage()
seed()

facility, df = get_facility_data('demo-1')
print("=== get_facility_data(demo-1) ===")
print("Facility name :", facility['name'])
print("Occupants     :", facility['occupants'])
print("Equipment     :", len(facility['equipment']), "items")
print("DataFrame rows:", len(df), "cols:", list(df.columns))
print("Peak energy   :", round(df['energy_kwh'].max(), 2), "kWh/hr")
night_mask = df['timestamp'].str[11:13].isin(['23','00','01','02','03','04'])
print("Night avg     :", round(df[night_mask]['energy_kwh'].mean(), 2), "kWh/hr (23-04)")
print("PASS: optimization owner can call get_facility_data() directly.")

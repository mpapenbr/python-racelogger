from racelogger.util.utils import collect_car_infos


class DriverProcessor():
    def __init__(self, current_ir=None) -> None:
        self.lookup = {}  # contains the current driver for a car
        self.team_member = {}  # contains all drivers who entered a car
        for d in current_ir['DriverInfo']['Drivers']:
            self.lookup[d['CarIdx']] = d.copy()
            self.team_member[d['CarIdx']] = [d.copy()]

    def process(self, ir, msg_proc=None, pit_proc=None):
        print(f"called with new driver info")
        # update lookup in any case
        for d in ir['DriverInfo']['Drivers']:
            if next((x for x in self.team_member[d['CarIdx']] if x['UserName'] == d['UserName']),  None) == None:
                self.team_member[d['CarIdx']].append(d.copy())
            if d['UserName'] != self.lookup[d['CarIdx']]['UserName']:
                self.lookup[d['CarIdx']] = d.copy()
                msg_proc.add_driver_enter_car(d['CarIdx'])
                # pit_proc.signal_driver_change(d['CarIdx'])

        pass

    def car_class(self, car_idx):
        return self.lookup[car_idx]['CarClassShortName']

    def car_class_id(self, car_idx):
        return self.lookup[car_idx]['CarClassID']

    def car(self, car_idx):
        return self.lookup[car_idx]['CarScreenNameShort']

    def car_id(self, car_idx):
        return self.lookup[car_idx]['CarID']

    def car_number(self, car_idx):
        return self.lookup[car_idx]['CarNumber']

    def car_num_raw(self, car_idx):
        return self.lookup[car_idx]['CarNumberRaw']

    def user_name(self, car_idx):
        return self.lookup[car_idx]['UserName']

    def team_name(self, car_idx):
        return self.lookup[car_idx]['TeamName']

    def driverdata_output(self):
        """returns a data structure to be send on the driver topic."""
        def real_entry(d): return d['IsSpectator'] == 0 and d['CarIsPaceCar'] == 0
        # x = collect_car_infos(filter(real_entry, list(self.lookup.values())))
        return {
            'carInfo': collect_car_infos(filter(real_entry, self.lookup.values())),
            'entries': [{
                'car': {
                    'carIdx': car_idx,
                    'name': self.car(car_idx),
                    'carId': self.car_id(car_idx),
                    'carClassId': self.car_class_id(car_idx),
                    'carNumber': self.car_number(car_idx),
                    'carNumberRaw': self.car_num_raw(car_idx),
                },
                'team': {
                    'carIdx': car_idx,
                    'name': self.team_name(car_idx),
                    'id': self.lookup[car_idx]['TeamID'],
                },
                'drivers': [{
                    'carIdx': d['CarIdx'],
                    'name': d['UserName'],
                    'id': d['UserID'],
                    'initials': d['Initials'],
                    'abbrevName': d['AbbrevName'],
                    'licString': d['LicString'],
                    'licLevel': d['LicLevel'],  # flattened combination of Level (R,D,C,..) + main value (1,2,3,4)
                    'licSubLevel': d['LicSubLevel'],  # 499 means 4.99
                    'iRating': d['IRating'],
                } for d in list(filter(real_entry, ir_data))]
            } for car_idx, ir_data in self.team_member.items() if real_entry(self.lookup[car_idx])]
        }

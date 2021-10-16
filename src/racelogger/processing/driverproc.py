class DriverProcessor():
    def __init__(self, current_ir=None) -> None:
        self.lookup = {}
        self.team_member = {}
        for d in current_ir['DriverInfo']['Drivers']:
            self.lookup[d['CarIdx']] = d.copy()
            self.team_member[d['CarIdx']] = [d.copy()]

    def process(self, ir, msg_proc=None, pit_proc=None):
        # TODO: detect changes in ir-drivers.

        print(f"called with new driver info")
        # update lookup in any case
        for d in ir['DriverInfo']['Drivers']:
            if next((x for x in self.team_member[d['CarIdx']] if  x['UserName'] == d['UserName']),  None) == None:
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

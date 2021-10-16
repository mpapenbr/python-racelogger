from irsdk import Flags
from irsdk import SessionState

SessionManifest = ['sessionTime', 'timeRemain', 'lapsRemain', 'flagState', 'timeOfDay', 'airTemp', 'airDensity', 'airPressure', 'trackTemp', 'windDir', 'windVel']

class SessionData:
    def __init__(self, ir) -> None:
        self.sessionTime = ir['SessionTime']
        self.timeRemain = ir['SessionTimeRemain']
        self.lapsRemain = ir['SessionLapsRemainEx']
        self.timeOfDay = ir['SessionTimeOfDay']
        self.airTemp = ir['AirTemp']
        self.airDensity = ir['AirDensity']
        self.airPressure = ir['AirPressure']
        self.trackTemp = ir['TrackTemp']
        self.windDir = ir['WindDir']
        self.windVel = ir['WindVel']
        self.flagState = ""
        if ir['SessionState'] == SessionState.racing:
            if ir['SessionFlags'] & Flags.start_hidden == Flags.start_hidden: # this seems to be true for spectators
                self.flagState = 'GREEN'
            if ir['SessionFlags'] >> 16 & Flags.green:
                self.flagState = 'GREEN'
            if ir['SessionFlags'] >> 16 & Flags.yellow:
                self.flagState = 'YELLO'
            if ir['SessionFlags'] >> 16 & Flags.checkered:
                self.flagState = 'CHECKERED'
            if ir['SessionFlags'] >> 16 & Flags.white:
                self.flagState = 'WHITE'
        elif ir['SessionState'] == SessionState.checkered:
            self.flagState = 'CHECKERED'
        elif ir['SessionState'] == SessionState.cool_down:
            self.flagState = 'CHECKERED'
        elif ir['SessionState'] == SessionState.get_in_car:
            self.flagState = 'PREP'
        elif ir['SessionState'] == SessionState.parade_laps:
            self.flagState = 'PARADE'
        elif ir['SessionState'] == SessionState.invalid:
            self.flagState = 'INVALID'
        else:
            self.flagState = 'NONE'




    def manifest_output(self):
        return [self.__getattribute__(x) for x in SessionManifest]


from racelogger.util.utils import collect_car_classes
from racelogger.util.utils import collect_car_infos


def test_car_infos_extractor():
    ir = [
        {
            'CarIdx': 1,
            'CarID': 1,
            'CarClassID': 1,
            'CarScreenName': 'BMW M4 GT3',
            'CarScreenNameShort': 'BMW GT3',
            'CarClassShortName': 'GT3',
            'CarClassMaxFuelPct': '1.000 %',
            'CarClassPowerAdjust': '1.000 %',
            'CarClassWeightPenalty': '0.000 kg',
            'CarClassDryTireSetLimit': '1 %'  # may be a bug in irsdk/telemetry: unit percent is wrong, but delivered that way
        },
        {
            'CarIdx': 2,
            'CarID': 2,
            'CarClassID': 1,
            'CarScreenName': 'Audi R8 GT3',
            'CarScreenNameShort': 'Audi GT3',
            'CarClassShortName': 'GT3',
            'CarClassMaxFuelPct': '1.000 %',
            'CarClassPowerAdjust': '1.000 %',
            'CarClassWeightPenalty': '0.000 kg',
            'CarClassDryTireSetLimit': '1 %'  # may be a bug in irsdk/telemetry: unit percent is wrong, but delivered that way
        },
        {
            'CarIdx': 3,
            'CarID': 3,
            'CarClassID': 2,
            'CarScreenName': 'Porsche 992 (Cup)',
            'CarScreenNameShort': 'Porsche 992',
            'CarClassShortName': 'CUP-Porsche',
            'CarClassMaxFuelPct': '0.99 %',
            'CarClassPowerAdjust': '0.90 %',
            'CarClassWeightPenalty': '1.500 kg',
            'CarClassDryTireSetLimit': '0 %'  # may be a bug in irsdk/telemetry: unit percent is wrong, but delivered that way
        },
        {
            'CarIdx': 4,
            'CarID': 3,
            'CarClassID': 2,
            'CarScreenName': 'Porsche 992 (Cup)',
            'CarScreenNameShort': 'Porsche 992',
            'CarClassShortName': 'CUP-Porsche',
            'CarClassMaxFuelPct': '0.99 %',
            'CarClassPowerAdjust': '0.90 %',
            'CarClassWeightPenalty': '1.500 kg',
            'CarClassDryTireSetLimit': '0 %'  # may be a bug in irsdk/telemetry: unit percent is wrong, but delivered that way
        },
    ]

    expect = [
        {
            'carId': 1,
            'carClassId': 1,
            'carClassName': 'GT3',
            'name': 'BMW M4 GT3',
            'nameShort': 'BMW GT3',
            'fuelPct': 1.0,
            'powerAdjust': 1.0,
            'weightPenalty': 0,
            'dryTireSets': 1,
        },
        {
            'carId': 2,
            'carClassId': 1,
            'carClassName': 'GT3',
            'name': 'Audi R8 GT3',
            'nameShort': 'Audi GT3',
            'fuelPct': 1.0,
            'powerAdjust': 1.0,
            'weightPenalty': 0,
            'dryTireSets': 1,
        },
        {
            'carId': 3,
            'carClassId': 2,
            'carClassName': 'CUP-Porsche',
            'name': 'Porsche 992 (Cup)',
            'nameShort': 'Porsche 992',
            'fuelPct': 0.99,
            'powerAdjust': 0.9,
            'weightPenalty': 1.5,
            'dryTireSets': 0,
        },

    ]
    result = collect_car_infos(ir)
    assert expect == result


def test_car_classes_extractor_standard():
    ir = [
        {
            'CarClassID': 1,
            'CarClassShortName': 'GT3',
        },
        {
            'CarClassID': 2,
            'CarClassShortName': 'GT4',
        },
    ]
    expect = [{'id': 1, 'name': 'GT3'}, {'id': 2, 'name': 'GT4'}]
    result = collect_car_classes(ir)


def test_car_classes_extractor_ai_simulation():
    ir = [
        {
            'CarClassID': 1,
            'CarClassShortName': '',
        },
        {
            'CarClassID': 2,
            'CarClassShortName': '',
        },
    ]
    expect = [{'id': 1, 'name': 'CarClass 1'}, {'id': 2, 'name': 'CarClass 2'}]
    result = collect_car_classes(ir)

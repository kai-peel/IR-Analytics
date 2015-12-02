from utils import irutils as ir
import json


def main():
    try:
        f = ir.Logger('cloud', 1)
        # res = ir.get_ir_pulses(6841)
        res = ir.get_ir_codeset(690254)
        # res = ir.get_ir_power(1, 50, '')
        # res = ir.get_ir_level1(1, 50, '')
        print json.dumps(res, indent=2, sort_keys=True)
        f.logs[0].write('%s' % json.dumps(res, indent=2, sort_keys=True))
    except Exception, e:
        print e

if __name__ == '__main__':
    main()
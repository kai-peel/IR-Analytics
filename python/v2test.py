from utils import irutils as ir
import json


def main():
    try:
        res = ir.get_ir_pulses(3456)
        #res = ir.get_ir_codeset(1004649)
        #res = ir.get_ir_power(1, 50, '')
        #res = ir.get_ir_level1(1, 50, '')
        print json.dumps(res, indent=2, sort_keys=True)

    except Exception, e:
        print e

if __name__ == '__main__':
    main()
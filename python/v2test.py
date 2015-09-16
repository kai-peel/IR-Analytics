from utils import irutils as ir
import json


def main():
    try:
        #res = ir.get_ir_stream2(269285)
        #res = ir.get_ir_codeset(390465)
        res = ir.get_ir_power(3, 31, 'CN')
        #res = ir.get_ir_level1(3, 31, 'CN')
        print json.dumps(res, indent=2, sort_keys=True)

    except Exception, e:
        print e

if __name__ == '__main__':
    main()
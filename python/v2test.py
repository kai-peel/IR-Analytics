from utils import irutils as ir
import json


def main():
    try:
        res = ir.get_ir_stream2(181946)
        print json.dumps(res, indent=4, sort_keys=True)

        res = ir.get_ir_codeset(1004194)
        print json.dumps(res, indent=4, sort_keys=True)

    except Exception, e:
        print e

if __name__ == '__main__':
    main()
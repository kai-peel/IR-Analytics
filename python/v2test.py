from utils import irutils as ir
import json


def main():
    try:
        res = ir.get_ir_stream2(215300)
        print json.dumps(res, indent=4, sort_keys=True)
        #print "========================================================================================================================"
        #res = ir.get_ir_codeset(390461)
        #print json.dumps(res, indent=4, sort_keys=True)

    except Exception, e:
        print e

if __name__ == '__main__':
    main()
from config import *
import datetime
from elasticsearch import Elasticsearch

class ElasticLogger():
    def __init__(self):
        self.es = Elasticsearch(
            'search-taunlp-j3hlsrtqkl2nndztdcypvdf7y4.us-east-1.es.amazonaws.com',
            port=80,
            use_ssl=False,
            verify_certs=False,
        )

        self.LOG_INDEX = "webkb_logs"
        self.LOG_LEVELS = ["INFO", "WARNING", "ERROR"]
        self.bulk_data = []
        self.LOG_BULK_SIZE = 1
        self.default_val_dict = {}

    def set_repeated_context_dict(self, run_tag, context_dict):
        self.default_val_dict['run_tag'] = run_tag
        for key in context_dict:
            self.default_val_dict[key] = context_dict[key]

    def write_log(self, level, message, context_dict={},push_bulk=True):
        if level == 'DEBUG_NN':
            LOG_INDEX = 'debug_nn'
        else:
            LOG_INDEX = self.LOG_INDEX
        fields_to_print = list(context_dict.keys())
        common_fields = {'log_timestamp': datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]}
        context_dict.update(common_fields)
        context_dict.update(self.default_val_dict)
        context_dict['message'] = message

        try:

            additional_text = " ".join([key + ': ' + str(context_dict[key]) + ',' for key in fields_to_print])

            print(level + '|' + context_dict['log_timestamp'] + ': ' + message )
            if len(additional_text) > 0:
                print(additional_text)

            if level=='ERROR':
                print(context_dict['stacktrace'])
        except:
            print('could not print log to screen')

        try:
            self.bulk_data.append({
                "index": {
                    "_index": LOG_INDEX,
                    "_type": level,
                }
            })

            self.bulk_data.append(context_dict)

            if (len(self.bulk_data) > self.LOG_BULK_SIZE * 2 or push_bulk) and config.use_cloud_logs:
                res = self.es.bulk(index=LOG_INDEX, body=self.bulk_data, refresh=True)
                self.bulk_data = []
                if res['errors']:
                    print("error writing logs!!")
        except:
            print("log failed!!!!!!!!!!!!!!!!")










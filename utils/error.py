from utils.db import save_file_response


def error_handler(email, file, res):
    if file and res:
        save_file_response(file, res)


error_codes = {'ME': print, 'FHE': print, 'VE': error_handler, 'VUNF': error_handler, 'VUWCNA': error_handler,
               'VUWCNF': error_handler, 'IC': error_handler, 'IO': error_handler, 'AE': error_handler,
               'ASE': error_handler, 'UIE': error_handler, 'UINF': error_handler, 'AUE': error_handler,
               'UE': error_handler, 'VFNE': error_handler, 'SGE': print}

error_responses = {'VE': [{'status': 'failed', 'status_message': 'Failed', 'message': ['Vault is down']},
                          {'error_code': 'VE', 'status_message': 'Failed', 'message': ['Unable to upload']}],
                   'VUNF': [{'status': 'failed', 'status_message': 'Failed', 'message': ['User not found on vault']},
                            {'error_code': 'VUNF', 'status_message': 'Failed', 'message': ['Unable to upload']}],
                   'VUWCNA': [{'status': 'failed', 'status_message': 'Failed',
                               'message': ['User word cloud not accessible on vault']},
                              {'error_code': 'VUWCNA', 'status_message': 'Failed', 'message': ['Unable to upload']}],
                   'VUWCNF': [{'status': 'failed', 'status_message': 'Failed',
                               'message': ['User word cloud not present on vault']},
                              {'error_code': 'VUWCNF', 'status_message': 'Failed', 'message': ['Unable to upload']}],
                   'AE': [{'status': 'failed', 'status_message': 'Failed', 'message': ['Unable to anonymize']},
                          {'error_code': 'AE', 'status_message': 'Failed', 'message': ['Unable to upload']}],
                   'ASE': [{'status': 'failed', 'status_message': 'Failed', 'message': ['Unable to anonymize']},
                           {'error_code': 'ASE', 'status_message': 'Failed', 'message': ['Unable to upload']}],
                   'UIE': [{'status': 'failed', 'status_message': 'Failed', 'message': ['Unable to anonymize']},
                           {'error_code': 'UIE', 'status_message': 'Failed', 'message': ['Unable to upload']}],
                   'UINF': [{'status': 'failed', 'status_message': 'Failed', 'message': ['Unable to anonymize']},
                            {'error_code': 'UINF', 'status_message': 'Failed', 'message': ['Unable to upload']}],
                   'AUE': [{'status': 'failed', 'status_message': 'Failed', 'message': ['Unable to anonymize']},
                           {'error_code': 'AUE', 'status_message': 'Failed', 'message': ['Unable to upload']}],
                   'UE': ['NA', {'error_code': 'UE', 'status_message': 'Failed', 'message': ['Unable to upload']}],
                   'VFNE': [{'status': 'failed', 'status_message': 'Failed', 'message': ['Unable to anonymize']},
                            {'error_code': 'VFNE', 'status_message': 'Failed', 'message': ['Unable to upload']}],
                   'IC': [{'status': 'failed', 'status_message': 'Failed', 'message': ['Unable to anonymize']},
                          {'error_code': 'IC', 'status_message': 'Failed', 'message': ['Unable to upload']}],
                   'IO': [{'status': 'failed', 'status_message': 'Failed', 'message': ['Unable to anonymize']},
                          {'error_code': 'IO', 'status_message': 'Failed', 'message': ['Unable to upload']}]}


def fetch_error_handler(m, num, e):
    # m.store(num, '+FLAGS', '\\SEEN'), # m.store(num, '-FLAGS', '\\SEEN')
    func_ = error_codes.get(str(e), print)
    func_(e)


def common_error_handler(e, email, file):
    func_ = error_codes.get(str(e), print)
    res_ = error_responses.get(str(e),
                               [{'status': 'failed', 'status_message': 'Failed', 'message': ['Unable to anonymize']},
                                {'error_code': str(e), 'status_message': 'Failed', 'message': ['Unable to upload']}])

    if str(func_).find('print') != -1:
        func_(e)
    else:
        func_(email, file, res_)

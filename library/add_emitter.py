def get_emitter_schema(emitter='ram-emitter', protocol='local', emit_keys=None, target_path=None):
    return {
        'emitter': {
            '_type': 'step',
            'address': f'{protocol}:{emitter}',
            'config': {
                'ports': {
                    'inputs': {
                        'data': 'tree[any]'
                    }
                }
            },
            'inputs': {
                'data': [] or target_path
            }
        }
    }
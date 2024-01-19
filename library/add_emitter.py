def get_emitter_schema(
        emitter='ram-emitter',
        protocol='local',
        emit_keys=None,  # TODO
        target_path=None
):
    return {
        'emitter': {
            '_type': 'step',
            'address': f'{protocol}:{emitter}',
            'config': {
                'inputs_schema': {
                    key: 'tree[any]' for key in emit_keys
                } if emit_keys else 'tree[any]'
            },
            'inputs': {'data': target_path},
            # 'inputs': [] or target_path,  # TODO make this work
        }
    }
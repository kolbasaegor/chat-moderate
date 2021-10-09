import json


def generate_package(author=None, name=None, version=None,
                     description=None, dependencies=None):
    package = dict(
        author=author if author is not None else 'nobody',
        name=name if name is not None else 'nobody',
        version=version if version is not None else '0.0.1',
        description=description if description is not None else '-',
        dependencies=dependencies if dependencies is not None else []
    )

    return json.dumps(package, indent=2, ensure_ascii=False)

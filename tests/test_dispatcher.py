import pytest

from embedded_sass_python import embedded_sass_pb2 as sass_pb
from embedded_sass_python.dispatcher import Dispatcher


@pytest.mark.asyncio
async def test_version() -> None:
    dispatcher = await Dispatcher.create()
    m = sass_pb.InboundMessage()
    m.version_request.id = 0
    response = await dispatcher.dispatch(m)
    assert response.version_response.implementation_name == 'Dart Sass'


@pytest.mark.asyncio
async def test_compile() -> None:
    dispatcher = await Dispatcher.create()
    m = sass_pb.InboundMessage()
    m.compile_request.string.source = '''
        .selector {
          margin: 1;

          .nested {
            margin: 2;
          }
        }
        '''
    # style, source_map, importers, global_functions, alert_color, alert_ascii, verbose, quiet_deps,
    # source_map_include_sources, charset
    response = await dispatcher.dispatch(m)
    expected = '.selector{margin:1;}.selector.nested{margin:2;}'
    assert ''.join(response.compile_response.success.css.split()) == expected

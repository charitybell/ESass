import asyncio

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
    response = await dispatcher.dispatch(m)
    expected = '.selector{margin:1;}.selector.nested{margin:2;}'
    assert ''.join(response.compile_response.success.css.split()) == expected


@pytest.mark.asyncio
async def test_multiple_requests() -> None:
    dispatcher = await Dispatcher.create()

    m1 = sass_pb.InboundMessage()
    m2 = sass_pb.InboundMessage()

    m1.compile_request.string.source = '.m1 { .nested { margin: 1; } }'
    m2.compile_request.string.source = '.m2 { .nested { margin: 2; } }'

    m1_expected = '.m1.nested{margin:1;}'
    m2_expected = '.m2.nested{margin:2;}'

    m1_response, m2_response = await asyncio.gather(
        dispatcher.dispatch(m1), dispatcher.dispatch(m2))

    assert ''.join(m1_response.compile_response.success.css.split()) == m1_expected
    assert ''.join(m2_response.compile_response.success.css.split()) == m2_expected


@pytest.mark.asyncio
async def test_multiple_sequential_requests() -> None:
    dispatcher = await Dispatcher.create()

    m1 = sass_pb.InboundMessage()
    m2 = sass_pb.InboundMessage()

    m1.compile_request.string.source = '.m1 { .nested { margin: 1; } }'
    m2.compile_request.string.source = '.m2 { .nested { margin: 2; } }'

    m1_expected = '.m1.nested{margin:1;}'
    m2_expected = '.m2.nested{margin:2;}'

    m1_response = await dispatcher.dispatch(m1)
    m2_response = await dispatcher.dispatch(m2)

    assert ''.join(m1_response.compile_response.success.css.split()) == m1_expected
    assert ''.join(m2_response.compile_response.success.css.split()) == m2_expected

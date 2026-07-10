from memory import InMemoryBackend, MemoryManager


def test_memory_store_search_and_forget() -> None:
    manager = MemoryManager(InMemoryBackend())
    manager.store('k1', 'Architecture uses plugins', tags=['architecture'])
    result = manager.search('plugins')
    assert result.total == 1
    manager.forget('k1')
    assert manager.retrieve('k1') is None

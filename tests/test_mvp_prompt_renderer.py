import pytest

from mvp.prompt_renderer import prompt_inputs, render_demo_prompt


@pytest.mark.parametrize(
    "name,package",
    [
        ("codex-cli-demo", "codex_cli_demo"),
        ("weather-tools", "weather_tools"),
        ("inventory-report", "inventory_report"),
    ],
)
def test_render_demo_prompt_materializes_inputs(name: str, package: str) -> None:
    prompt = render_demo_prompt(
        project_name=name, demo_description="A bounded useful description"
    )
    inputs = prompt_inputs(name, "A bounded useful description")
    assert inputs.package_name == package
    assert f"Project name: `{name}`" in prompt
    assert f"Python package name: `{package}`" in prompt
    assert "A bounded useful description" in prompt
    assert "generated-demo" in prompt


@pytest.mark.parametrize("name", ["BadName", "bad_name", "-bad", "bad--name"])
def test_render_demo_prompt_rejects_invalid_names(name: str) -> None:
    with pytest.raises(ValueError):
        render_demo_prompt(project_name=name, demo_description="ok")


def test_render_demo_prompt_rejects_reserved_canonical_name() -> None:
    with pytest.raises(ValueError, match="reserved"):
        render_demo_prompt(project_name="hello-codex", demo_description="ok")
    with pytest.raises(ValueError, match="reserved"):
        prompt_inputs("hello-codex", "ok")


@pytest.mark.parametrize(
    "description",
    ["x" * 501, "bad\rdesc", "```breakout```", "${{ secrets.OPENAI_API_KEY }}"],
)
def test_render_demo_prompt_rejects_unsafe_descriptions(description: str) -> None:
    with pytest.raises(ValueError):
        render_demo_prompt(project_name="codex-cli-demo", demo_description=description)

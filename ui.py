import flet as ft
from types import SimpleNamespace
from chatbot import askModel, getModelsName

# Define font configurations
JetBrainsMono = SimpleNamespace(
    fontName="JetBrainsMono",
    fontURL="https://raw.githubusercontent.com/JetBrains/JetBrainsMono/master/fonts/ttf/JetBrainsMono-Regular.ttf",
)
Ubuntu = SimpleNamespace(
    fontName="Ubuntu",
    fontURL="https://github.com/google/fonts/raw/refs/heads/main/ufl/ubuntu/Ubuntu-Regular.ttf",
)


async def main(page: ft.Page):
    # Center alignment for the page content
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    models_name = await getModelsName()

    # Clear chat content
    def clear_chat(e):
        answer_container.content.controls.clear()
        page.update()

    # Set up fonts and theme
    page.fonts = {
        JetBrainsMono.fontName: JetBrainsMono.fontURL,
        Ubuntu.fontName: Ubuntu.fontURL,
    }
    page.theme = ft.Theme(font_family=JetBrainsMono.fontName)
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.icons.CHAT_ROUNDED, color="#f1f5f9"),
        title=ft.Text("Chat Bot", color="#f1f5f9", font_family=Ubuntu.fontName),
        actions=[
            ft.IconButton(
                ft.icons.CLEAR_ALL_ROUNDED,
                icon_color="#f8fafc",
                tooltip="Clear Chat",
                on_click=clear_chat,
            )
        ],
        title_spacing=0,
    )

    # Append user input to chat
    def append_input(_input: str):
        if _input:
            answer_container.content.controls.append(
                ft.Row(
                    controls=[
                        ft.Container(
                            expand=True,
                            bgcolor="#151a1e",
                            content=ft.Markdown(
                                value=_input,
                                selectable=True,
                                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                                code_theme=ft.MarkdownCodeTheme.ATOM_ONE_DARK,
                                img_error_content=ft.Text("Can't Load Image."),
                            ),
                            padding=10,
                            border_radius=8,
                        ),
                    ],
                ),
            )
            page.update()

    # Handle sending messages
    async def on_send(text_value: str):
        model_name = model_name_dropdown.value
        user_question.value = ""
        append_input(f"User: {text_value}")
        if model_name and text_value:
            loading_spinner = ft.ProgressRing(visible=True, expand=False)
            answer_container.content.controls.append(loading_spinner)
            page.update()
            response = await askModel(modelName=model_name, prompt=text_value)
            loading_spinner.visible = False
            answer_container.content.controls.remove(loading_spinner)
            page.update()
            append_input(f"ChatBot:\n{response['response']}")
            with open("chatbot.txt", "a", encoding="utf-8") as f:
                f.write(f"{response['response']}\n-------------------------------\n")

    # Click handler for the submit button
    async def on_click_handler(e):
        submit_button.disabled = True
        page.update()
        await on_send(user_question.value)
        submit_button.disabled = False
        page.update()

    # Initialize UI elements first
    model_name_dropdown = ft.Dropdown(
        value="gemma2:2b",
        options=[ft.dropdown.Option(text=model_name) for model_name in models_name],
    )

    user_question = ft.TextField(
        expand=True,
        multiline=True,
        max_lines=3,
        hint_text="Message ChatBot",
    )

    submit_button = ft.ElevatedButton(
        height=50,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(2),
            bgcolor="#818cf8",
        ),
        on_click=on_click_handler,
        content=ft.Text(
            "Send",
            scale=2,
            font_family=Ubuntu.fontName,
            color="#f8fafc",
        ),
    )

    answer_container = ft.Container(
        bgcolor="#20282d",
        width=page.width,
        height=page.height * 0.75,
        content=ft.ListView(
            padding=ft.padding.symmetric(10, 10),
            controls=[],
            height=page.height * 0.75,
            spacing=5,
        ),
    )

    # Main container with UI elements
    main_container = ft.Container(
        width=page.width,
        height=page.height,
        bgcolor="#15191e",
        alignment=ft.alignment.center,
        content=ft.Column(
            expand=True,
            spacing=2,
            controls=[
                model_name_dropdown,
                ft.Row(
                    spacing=2,
                    controls=[user_question, submit_button],
                ),
                answer_container,
            ],
        ),
    )
    page.add(main_container)


if __name__ == "__main__":
    ft.app(main)

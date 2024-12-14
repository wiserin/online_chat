from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import run_async, run_js

import asyncio

messages = []
online_users = set()

MAX_MESSAGES = 100

async def main():
    global messages

    put_markdown('Это чат')

    msg_box = output()
    put_scrollable(msg_box, height=300, keep_bottom=True)

    name = await input('Войти в чат', required=True, placeholder='Имя', validate=lambda n: 'Ты не настолько умный' if n in online_users else None)
    online_users.add(name)
    messages.append((f'{name} зашел к нам'))
    msg_box.append(put_markdown((f'{name} зашел к нам')))

    refresh_task = run_async(refresh_msg(name, msg_box))

    while True:
        data = await input_group('Новое сообщение', [
            input(placeholder='Ваш текст', name="msg"),
            actions(name='cmd', buttons=['Отправить', {'label':'Выйти', 'type':'cancel'}])
        ], validate=lambda m: ('msg', 'Введите текст') if m['cmd'] == 'Отправить' and not m['msg'] else None)

        if data is None:
            break

        msg_box.append(put_markdown(f'{name} : {data["msg"]}'))
        messages.append((name, data['msg']))

    refresh_task.close()

    online_users.remove(name)
    toast('Вы покинули нас.')
    msg_box.append(put_markdown(f'{name} кинул нас'))
    messages.append((f'{name} кинул нас'))

    put_button(['Вернуться'], onclick=lambda btn: run_js('windows.location.reload('))

async def refresh_msg(name, msg_box):
    global messages
    last_idx = len(messages)

    while True:
        await asyncio.sleep(1)

        for m in messages[last_idx:]:
            if m[0] != name:
                msg_box.append(put_markdown(f'{m[0]} : {m[1]}'))

        if len(messages) > MAX_MESSAGES:
            messages = messages[len(messages) // 2]

        last_idx = len(messages)
                

if __name__ == "__main__":
    start_server(main, debug=True, port=0, host='0.0.0.0', cdn=False)
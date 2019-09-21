from talon.voice import Context, Key, press
ctx = Context('chromestuff')
def switch_tab(m):
    num = m['chromestuff.number'][0]
    press(f'cmd-{num}')

ctx.keymap({
    'chrome switch {chromestuff.number}': switch_tab,
})
ctx.set_list('number', [str(n) for n in [1, 2, 3, 4, 5, 6, 7, 8, 9]])
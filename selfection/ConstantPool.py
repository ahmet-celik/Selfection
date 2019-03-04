import re


class ConstantPool(object):
    # Generate callgraph using objdump and readelf
    # arm-none-eabi-objdump and arm-none-eabi-readelf should be in PATH.
    ARMPREFIX = "arm-none-eabi-"
    READELF = ARMPREFIX + "readelf {} --symbols -W"
    OBJDUMP = ARMPREFIX + "objdump -j .text -d {}"
    SECTIONS = ARMPREFIX + "readelf {} -S -W"
    # Matches '00000370 <up_lowsetup>:'
    FUNC_ENTRY = re.compile(r"^([a-f0-9]{8}) <(.*)>:$")
    # Matches '     310:       f000 f940       bl      594 <up_earlyserialinit>'
    FUNC_CALL = re.compile(r"^ {,7}[a-f0-9]+:\s([a-f0-9]{4} ){1,2}\sbl\s([a-f0-9]+) <(.*?)>$")
    # Matches ' 4115210:	eb01cc75 	bl	41883ec <getpeername>'
    FUNC_CALL_2 = re.compile(r"^ {,7}[a-f0-9]+:\s([a-f0-9]{8} )\sbl\s([a-f0-9]+) <(.*?)>$")  # for board
    # Matches 'tc_libc_misc_crc8part'
    FUNC_TEST = re.compile(r"^[ui]?tc_")
    # Matches '   11186:       4b06            ldr     r3, [pc, #24]   ; (111a0 <tc_libc_misc_crc8part+0x74>)'
    INS_LINE = re.compile(r"^ {,7}[a-f0-9]+:\s([a-f0-9]{4} ){1,2}\s(\S+\s[^;]*?)(?:;.*?)?$")
    # Matches ' 411521c:	e59f304c 	ldr	r3, [pc, #76]	; 4115270 <tc_net_getpeername_p+0x78>'
    INS_LINE_2 = re.compile(r"^ {,7}[a-f0-9]+:\s([a-f0-9]{8} )\s(\S+\s[^;]*?)(?:;.*?)?$")
    # Matches '   1119c:       0003f40a        .word   0x0003f40a'
    DATA_LINE = re.compile(r"^ {,7}[a-f0-9]+:\s([a-f0-9]{8} )\s(\.word\s[^;]*?)(?:;.*?)?$")
    # Matches 'beq.n   2cc <exception_common+0x30>'
    # Replace to 'b\1 \3'
    BRANCH_LINE = re.compile(r"^b(l?(?:eq|ne|cs|cc|mi|pl|vs|vc|hi|ls|ge|lt|gt|le)?)(?:\.(?:w|b|n|h))?\s*([a-f0-9]+) <(.*)>$")
    # Matches 'cbz     r1, 4a2 <up_rxint+0x14>'
    # Replace to '\1 \2, \4'
    CONDITIONAL_BRANCH_LINE = re.compile(r"^(cbn?z)\s*([^,]*), ([a-f0-9]+) <(.*)>$")
    # Matches '  [ 2] .text             PROGBITS        040c8020 008020 1576ef 00  AX  0   0 32'
    SECTION_LINE = re.compile(r"^\s{,2}\[\s{,1}(?P<nr>\S*)\]\s(?P<name>\S*)\s{,25}"
                              r"(?P<type>\S*)\s{,41}\s(?P<addr>[0-9a-f]{8})\s"
                              r"(?P<off>[0-9a-f]{,8})\s(?P<size>[0-9a-f]{,8})\s.*$")


def test_regex(regex, repl, text, new_text):
    result = regex.sub(repl, text)
    print result
    assert result == new_text, "Error for regex '{}'".format(regex.pattern)


if __name__ == '__main__':
    test_regex(ConstantPool.FUNC_ENTRY, "\\2", "000377a8 <__aeabi_dmul>:", "__aeabi_dmul")
    test_regex(ConstantPool.FUNC_CALL, "\\3", "     310:\tf000 f940 \tbl 594 <up_earlyserialinit>", "up_earlyserialinit")
    test_regex(ConstantPool.FUNC_TEST, "g", "tc_libc_misc_stdio", "glibc_misc_stdio")
    test_regex(ConstantPool.FUNC_TEST, "g", "itc_libc_misc_stdio", "glibc_misc_stdio")
    test_regex(ConstantPool.FUNC_TEST, "g", "utc_libc_misc_stdio", "glibc_misc_stdio")
    test_regex(ConstantPool.INS_LINE, "\\2", "   11186:\t4b06 \tldr\tr3, [pc, #24]\t; "
                                             "(111a0 <tc_libc_misc_crc8part+0x74>)",
               "ldr\tr3, [pc, #24]\t")
    test_regex(ConstantPool.DATA_LINE, "\\2", "   1119c:\t0003f40a \t.word\t0x0003f40a", ".word\t0x0003f40a")
    test_regex(ConstantPool.BRANCH_LINE, "b\\1 \\3", "beq.n   379ae <__aeabi_dmul+0x206>", "beq __aeabi_dmul+0x206")
    test_regex(ConstantPool.BRANCH_LINE, "b\\1 \\3", "bl 594 <up_earlyserialinit>", "bl up_earlyserialinit")
    test_regex(ConstantPool.BRANCH_LINE, "b\\1 \\3", "b.w     1d38 <irq_attach>", "b irq_attach")
    test_regex(ConstantPool.BRANCH_LINE, "b\\1 \\3", "bleq    37984 <__aeabi_dmul+0x1dc>", "bleq __aeabi_dmul+0x1dc")
    test_regex(ConstantPool.CONDITIONAL_BRANCH_LINE, "\\1 \\2, \\4", "cbz     r6, 384d0 <__udivmoddi4+0xa0>",
               "cbz r6, __udivmoddi4+0xa0")
    test_regex(ConstantPool.CONDITIONAL_BRANCH_LINE, "\\1 \\2, \\4", "cbnz    r4, 3875c <sched_mergepending+0x48>",
               "cbnz r4, sched_mergepending+0x48")



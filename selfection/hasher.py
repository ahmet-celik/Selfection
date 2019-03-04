import zlib
from ConstantPool import ConstantPool


def checksum(data):
    return zlib.adler32(data)


def checksum_incremental(data, prev_checksum):
    return zlib.adler32(data, prev_checksum)


def checksum_ins_line(line, prev_checksum):
    m = ConstantPool.DATA_LINE.match(line)
    if m:
        return prev_checksum
    else:
        m = ConstantPool.INS_LINE.match(line)
        if m:
            return process_insn_line(m, prev_checksum)
        else:
            m = ConstantPool.INS_LINE_2.match(line)
            if m:
                return process_insn_line(m, prev_checksum)
            else:
                return prev_checksum


def process_insn_line(m, prev_checksum):
    insn = m.group(2).strip()
    m = ConstantPool.BRANCH_LINE.match(insn)
    if m:
        return checksum_incremental("b{} {}".format(m.group(1), m.group(3)), prev_checksum)
    else:
        m = ConstantPool.CONDITIONAL_BRANCH_LINE.match(insn)
        if m:
            return checksum_incremental("{} {}, {}".format(m.group(1), m.group(2), m.group(4)), prev_checksum)
        else:
            return checksum_incremental(insn, prev_checksum)


# Code for <__aeabi_dmul>:
ARM_CODE_0 = """   377a8:	b570      	push	{r4, r5, r6, lr}
   377aa:	f04f 0cff 	mov.w	ip, #255	; 0xff
   377ae:	f44c 6ce0 	orr.w	ip, ip, #1792	; 0x700
   377b2:	ea1c 5411 	ands.w	r4, ip, r1, lsr #20
   377b6:	bf1d      	ittte	ne
   377b8:	ea1c 5513 	andsne.w	r5, ip, r3, lsr #20
   377bc:	ea94 0f0c 	teqne	r4, ip
   377c0:	ea95 0f0c 	teqne	r5, ip
   377c4:	f000 f8de 	bleq	37984 <__aeabi_dmul+0x1dc>
   377c8:	442c      	add	r4, r5
   377ca:	ea81 0603 	eor.w	r6, r1, r3
   377ce:	ea21 514c 	bic.w	r1, r1, ip, lsl #21
   377d2:	ea23 534c 	bic.w	r3, r3, ip, lsl #21
   377d6:	ea50 3501 	orrs.w	r5, r0, r1, lsl #12
   377da:	bf18      	it	ne
   377dc:	ea52 3503 	orrsne.w	r5, r2, r3, lsl #12
   377e0:	f441 1180 	orr.w	r1, r1, #1048576	; 0x100000
   377e4:	f443 1380 	orr.w	r3, r3, #1048576	; 0x100000
   377e8:	d038      	beq.n	3785c <__aeabi_dmul+0xb4>
   377ea:	fba0 ce02 	umull	ip, lr, r0, r2
   377ee:	f04f 0500 	mov.w	r5, #0
   377f2:	fbe1 e502 	umlal	lr, r5, r1, r2
   377f6:	f006 4200 	and.w	r2, r6, #2147483648	; 0x80000000
   377fa:	fbe0 e503 	umlal	lr, r5, r0, r3
   377fe:	f04f 0600 	mov.w	r6, #0
   37802:	fbe1 5603 	umlal	r5, r6, r1, r3
   37806:	f09c 0f00 	teq	ip, #0
   3780a:	bf18      	it	ne
   3780c:	f04e 0e01 	orrne.w	lr, lr, #1
   37810:	f1a4 04ff 	sub.w	r4, r4, #255	; 0xff
   37814:	f5b6 7f00 	cmp.w	r6, #512	; 0x200
   37818:	f564 7440 	sbc.w	r4, r4, #768	; 0x300
   3781c:	d204      	bcs.n	37828 <__aeabi_dmul+0x80>
   3781e:	ea5f 0e4e 	movs.w	lr, lr, lsl #1
   37822:	416d      	adcs	r5, r5
   37824:	eb46 0606 	adc.w	r6, r6, r6
   37828:	ea42 21c6 	orr.w	r1, r2, r6, lsl #11
   3782c:	ea41 5155 	orr.w	r1, r1, r5, lsr #21
   37830:	ea4f 20c5 	mov.w	r0, r5, lsl #11
   37834:	ea40 505e 	orr.w	r0, r0, lr, lsr #21
   37838:	ea4f 2ece 	mov.w	lr, lr, lsl #11
   3783c:	f1b4 0cfd 	subs.w	ip, r4, #253	; 0xfd
   37840:	bf88      	it	hi
   37842:	f5bc 6fe0 	cmphi.w	ip, #1792	; 0x700
   37846:	d81e      	bhi.n	37886 <__aeabi_dmul+0xde>
   37848:	f1be 4f00 	cmp.w	lr, #2147483648	; 0x80000000
   3784c:	bf08      	it	eq
   3784e:	ea5f 0e50 	movseq.w	lr, r0, lsr #1
   37852:	f150 0000 	adcs.w	r0, r0, #0
   37856:	eb41 5104 	adc.w	r1, r1, r4, lsl #20
   3785a:	bd70      	pop	{r4, r5, r6, pc}
   3785c:	f006 4600 	and.w	r6, r6, #2147483648	; 0x80000000
   37860:	ea46 0101 	orr.w	r1, r6, r1
   37864:	ea40 0002 	orr.w	r0, r0, r2
   37868:	ea81 0103 	eor.w	r1, r1, r3
   3786c:	ebb4 045c 	subs.w	r4, r4, ip, lsr #1
   37870:	bfc2      	ittt	gt
   37872:	ebd4 050c 	rsbsgt	r5, r4, ip
   37876:	ea41 5104 	orrgt.w	r1, r1, r4, lsl #20
   3787a:	bd70      	popgt	{r4, r5, r6, pc}
   3787c:	f441 1180 	orr.w	r1, r1, #1048576	; 0x100000
   37880:	f04f 0e00 	mov.w	lr, #0
   37884:	3c01      	subs	r4, #1
   37886:	f300 80ab 	bgt.w	379e0 <__aeabi_dmul+0x238>
   3788a:	f114 0f36 	cmn.w	r4, #54	; 0x36
   3788e:	bfde      	ittt	le
   37890:	2000      	movle	r0, #0
   37892:	f001 4100 	andle.w	r1, r1, #2147483648	; 0x80000000
   37896:	bd70      	pople	{r4, r5, r6, pc}
   37898:	f1c4 0400 	rsb	r4, r4, #0
   3789c:	3c20      	subs	r4, #32
   3789e:	da35      	bge.n	3790c <__aeabi_dmul+0x164>
   378a0:	340c      	adds	r4, #12
   378a2:	dc1b      	bgt.n	378dc <__aeabi_dmul+0x134>
   378a4:	f104 0414 	add.w	r4, r4, #20
   378a8:	f1c4 0520 	rsb	r5, r4, #32
   378ac:	fa00 f305 	lsl.w	r3, r0, r5
   378b0:	fa20 f004 	lsr.w	r0, r0, r4
   378b4:	fa01 f205 	lsl.w	r2, r1, r5
   378b8:	ea40 0002 	orr.w	r0, r0, r2
   378bc:	f001 4200 	and.w	r2, r1, #2147483648	; 0x80000000
   378c0:	f021 4100 	bic.w	r1, r1, #2147483648	; 0x80000000
   378c4:	eb10 70d3 	adds.w	r0, r0, r3, lsr #31
   378c8:	fa21 f604 	lsr.w	r6, r1, r4
   378cc:	eb42 0106 	adc.w	r1, r2, r6
   378d0:	ea5e 0e43 	orrs.w	lr, lr, r3, lsl #1
   378d4:	bf08      	it	eq
   378d6:	ea20 70d3 	biceq.w	r0, r0, r3, lsr #31
   378da:	bd70      	pop	{r4, r5, r6, pc}
   378dc:	f1c4 040c 	rsb	r4, r4, #12
   378e0:	f1c4 0520 	rsb	r5, r4, #32
   378e4:	fa00 f304 	lsl.w	r3, r0, r4
   378e8:	fa20 f005 	lsr.w	r0, r0, r5
   378ec:	fa01 f204 	lsl.w	r2, r1, r4
   378f0:	ea40 0002 	orr.w	r0, r0, r2
   378f4:	f001 4100 	and.w	r1, r1, #2147483648	; 0x80000000
   378f8:	eb10 70d3 	adds.w	r0, r0, r3, lsr #31
   378fc:	f141 0100 	adc.w	r1, r1, #0
   37900:	ea5e 0e43 	orrs.w	lr, lr, r3, lsl #1
   37904:	bf08      	it	eq
   37906:	ea20 70d3 	biceq.w	r0, r0, r3, lsr #31
   3790a:	bd70      	pop	{r4, r5, r6, pc}
   3790c:	f1c4 0520 	rsb	r5, r4, #32
   37910:	fa00 f205 	lsl.w	r2, r0, r5
   37914:	ea4e 0e02 	orr.w	lr, lr, r2
   37918:	fa20 f304 	lsr.w	r3, r0, r4
   3791c:	fa01 f205 	lsl.w	r2, r1, r5
   37920:	ea43 0302 	orr.w	r3, r3, r2
   37924:	fa21 f004 	lsr.w	r0, r1, r4
   37928:	f001 4100 	and.w	r1, r1, #2147483648	; 0x80000000
   3792c:	fa21 f204 	lsr.w	r2, r1, r4
   37930:	ea20 0002 	bic.w	r0, r0, r2
   37934:	eb00 70d3 	add.w	r0, r0, r3, lsr #31
   37938:	ea5e 0e43 	orrs.w	lr, lr, r3, lsl #1
   3793c:	bf08      	it	eq
   3793e:	ea20 70d3 	biceq.w	r0, r0, r3, lsr #31
   37942:	bd70      	pop	{r4, r5, r6, pc}
   37944:	f094 0f00 	teq	r4, #0
   37948:	d10f      	bne.n	3796a <__aeabi_dmul+0x1c2>
   3794a:	f001 4600 	and.w	r6, r1, #2147483648	; 0x80000000
   3794e:	0040      	lsls	r0, r0, #1
   37950:	eb41 0101 	adc.w	r1, r1, r1
   37954:	f411 1f80 	tst.w	r1, #1048576	; 0x100000
   37958:	bf08      	it	eq
   3795a:	3c01      	subeq	r4, #1
   3795c:	d0f7      	beq.n	3794e <__aeabi_dmul+0x1a6>
   3795e:	ea41 0106 	orr.w	r1, r1, r6
   37962:	f095 0f00 	teq	r5, #0
   37966:	bf18      	it	ne
   37968:	4770      	bxne	lr
   3796a:	f003 4600 	and.w	r6, r3, #2147483648	; 0x80000000
   3796e:	0052      	lsls	r2, r2, #1
   37970:	eb43 0303 	adc.w	r3, r3, r3
   37974:	f413 1f80 	tst.w	r3, #1048576	; 0x100000
   37978:	bf08      	it	eq
   3797a:	3d01      	subeq	r5, #1
   3797c:	d0f7      	beq.n	3796e <__aeabi_dmul+0x1c6>
   3797e:	ea43 0306 	orr.w	r3, r3, r6
   37982:	4770      	bx	lr
   37984:	ea94 0f0c 	teq	r4, ip
   37988:	ea0c 5513 	and.w	r5, ip, r3, lsr #20
   3798c:	bf18      	it	ne
   3798e:	ea95 0f0c 	teqne	r5, ip
   37992:	d00c      	beq.n	379ae <__aeabi_dmul+0x206>
   37994:	ea50 0641 	orrs.w	r6, r0, r1, lsl #1
   37998:	bf18      	it	ne
   3799a:	ea52 0643 	orrsne.w	r6, r2, r3, lsl #1
   3799e:	d1d1      	bne.n	37944 <__aeabi_dmul+0x19c>
   379a0:	ea81 0103 	eor.w	r1, r1, r3
   379a4:	f001 4100 	and.w	r1, r1, #2147483648	; 0x80000000
   379a8:	f04f 0000 	mov.w	r0, #0
   379ac:	bd70      	pop	{r4, r5, r6, pc}
   379ae:	ea50 0641 	orrs.w	r6, r0, r1, lsl #1
   379b2:	bf06      	itte	eq
   379b4:	4610      	moveq	r0, r2
   379b6:	4619      	moveq	r1, r3
   379b8:	ea52 0643 	orrsne.w	r6, r2, r3, lsl #1
   379bc:	d019      	beq.n	379f2 <__aeabi_dmul+0x24a>
   379be:	ea94 0f0c 	teq	r4, ip
   379c2:	d102      	bne.n	379ca <__aeabi_dmul+0x222>
   379c4:	ea50 3601 	orrs.w	r6, r0, r1, lsl #12
   379c8:	d113      	bne.n	379f2 <__aeabi_dmul+0x24a>
   379ca:	ea95 0f0c 	teq	r5, ip
   379ce:	d105      	bne.n	379dc <__aeabi_dmul+0x234>
   379d0:	ea52 3603 	orrs.w	r6, r2, r3, lsl #12
   379d4:	bf1c      	itt	ne
   379d6:	4610      	movne	r0, r2
   379d8:	4619      	movne	r1, r3
   379da:	d10a      	bne.n	379f2 <__aeabi_dmul+0x24a>
   379dc:	ea81 0103 	eor.w	r1, r1, r3
   379e0:	f001 4100 	and.w	r1, r1, #2147483648	; 0x80000000
   379e4:	f041 41fe 	orr.w	r1, r1, #2130706432	; 0x7f000000
   379e8:	f441 0170 	orr.w	r1, r1, #15728640	; 0xf00000
   379ec:	f04f 0000 	mov.w	r0, #0
   379f0:	bd70      	pop	{r4, r5, r6, pc}
   379f2:	f041 41fe 	orr.w	r1, r1, #2130706432	; 0x7f000000
   379f6:	f441 0178 	orr.w	r1, r1, #16252928	; 0xf80000
   379fa:	bd70      	pop	{r4, r5, r6, pc}


"""
ARM_CODE_1 = """   37c78:	f84d ed08 	str.w	lr, [sp, #-8]!
   37c7c:	f7ff fff4 	bl	37c68 <__aeabi_cdcmpeq>
   37c80:	bf0c      	ite	eq
   37c82:	2001      	moveq	r0, #1
   37c84:	2000      	movne	r0, #0
   37c86:	f85d fb08 	ldr.w	pc, [sp], #8
   37c8a:	bf00      	nop

"""


def checksum_text(text):
    checksum = 1
    for line in text.splitlines():
        checksum = checksum_ins_line(line, checksum)
    return checksum


if __name__ == '__main__':
    assert checksum_text(ARM_CODE_0) == -586905419, "Checksum mismatches!"
    assert checksum_text(ARM_CODE_1) == -1160701200, "Checksum mismatches!"

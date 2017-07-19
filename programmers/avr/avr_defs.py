

class Avr:

    AVR_ANSWER_BYTE = 0xAA

    #
    # Programming enable instruction
    #
    AVR_PROG_EN_B1 = 0xAC
    AVR_PROG_EN_B2 = 0x53
    AVR_PROG_EN_B3 = 0x00
    AVR_PROG_EN_B4 = 0x00

    #
    # Mass erase instruction
    #
    AVR_CHP_ERS_B1 = 0xAC
    AVR_CHP_ERS_B2 = 0x80
    AVR_CHP_ERS_B3 = 0x00
    AVR_CHP_ERS_B4 = 0x00

    #
    #	Status poll instruction
    #	Fourth byte is the answer
    #
    AVR_POLL_B1 = 0xF0
    AVR_POLL_B2 = 0x00
    AVR_POLL_B3 = 0x00
    AVR_POLL_B4 = AVR_ANSWER_BYTE


    #
    #  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #							LOAD INSTRUCTIONS
    #  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #


    #
    #	Load extended address instruction
    #	Third byte is extended address
    #
    AVR_LD_EXT_ADDR_B1	 = 0x4D
    AVR_LD_EXT_ADDR_B2	 = 0x00
    AVR_LD_EXT_ADDR_B4	 = 0x00

    #
    # Load program memory high byte
    # Second byte is addr MSB
    # Third byte is addr  LSB
    # Fourth byte is data high byte
    #
    AVR_LD_HPG_MEM_B1 = 0x48

    #
    # Load program memory low byte
    # Second byte is addr MSB
    # Third byte is addr  LSB
    # Fourth byte is data low byte
    #
    AVR_LD_LPG_MEM_B1 = 0x40


    #
    # Load EEPROM memory page instruction
    # Third byte is addr LSB
    # Fourth byte is data byte
    #
    AVR_LD_EMEM_B1	= 0xC1
    AVR_LD_EMEM_B2	= 0x00



    #
    #  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #							READ INSTRUCTIONS
    #  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #


    #
    #	Read program memory high byte
    #	Second byte is addr MSB
    #	Third byte is addr LSB
    #	Fourth byte is high byte answer
    #
    AVR_RD_HPG_MEM_B1 = 0x28
    AVR_RD_HPG_MEM_B4 = AVR_ANSWER_BYTE

    #
    #	Read program memory low byte
    #	Second byte is addr MSB
    #	Third byte is addr LSB
    #	Fourth byte is low byte answer
    #
    AVR_RD_LPG_MEM_B1 = 0x20
    AVR_RD_LPG_MEM_B4 = AVR_ANSWER_BYTE

    #
    # Read EEPROM memory
    # Second byte is addr MSB
    # Third byte is addr LSB
    # Fourth byte is answer
    #
    AVR_RD_EMEM_B1	= 0xA0
    AVR_RD_EMEM_B4	= AVR_ANSWER_BYTE

    #
    #	Read lock bits
    #
    AVR_RD_LCK_B1 = 0x58
    AVR_RD_LCK_B2 = 0x00
    AVR_RD_LCK_B3 = 0x00
    AVR_RD_LCK_B4 = AVR_ANSWER_BYTE

    #
    # Read signature byte
    # LSB bits of third byte[1:0] used for address
    # Mask is used to set only last bits
    #
    AVR_RD_SIG_B1	=       0x30
    AVR_RD_SIG_B2	=       0x00
    AVR_RD_SIG_B4	=	0x00 #AVR_ANSWER_BYTE
    AVR_RD_VENDOR_CODE	=	0x00
    AVR_RD_PART_FAMILY	=	0x01
    AVR_RD_PART_NUMBER	=	0x02

    #
    # Read fuse bits (as I understand LOW fuse)
    #
    AVR_RD_LFUSE_B1 = 0x50
    AVR_RD_LFUSE_B2 = 0x00
    AVR_RD_LFUSE_B3 = 0x00
    AVR_RD_LFUSE_B4 = AVR_ANSWER_BYTE

    #
    # Read high fuse bits
    #
    AVR_RD_HFUSE_B1 = 0x58
    AVR_RD_HFUSE_B2 = 0x08
    AVR_RD_HFUSE_B3 = 0x00
    AVR_RD_HFUSE_B4 = AVR_ANSWER_BYTE

    #
    # Read extended fuse bits
    #
    AVR_RD_EXFUSE_B1 = 0x50
    AVR_RD_EXFUSE_B2 = 0x08
    AVR_RD_EXFUSE_B3 = 0x00
    AVR_RD_EXFUSE_B4 = AVR_ANSWER_BYTE

    #
    #	Read calibration byte
    #	Third byte consists from magic symbols
    #	Read the datasheet
    #
    AVR_RD_CAL_B1 = 0x38
    AVR_RD_CAL_B2 = 0x00
    AVR_RD_CAL_B4 = AVR_ANSWER_BYTE


    #
    #  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #							WRITE INSTRUCTIONS
    #  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #


    #
    # Write program memory page
    # Second byte LSB bits[4:0] of MSB address
    # Third byte MSB bits[7:6]	os MSB address
    #
    AVR_WRT_MEM_B1 = 0x4C
    AVR_WRT_MEM_B4 = 0x00
    AVR_WRT_MEM_RSHIFT = 2
    AVR_WRT_MEM_LSHIFT = 6
    AVR_WRT_MEM_B2_MASK = 0x1F
    AVR_WRT_MEM_B3_MASK = 0xC0


    #
    # Write EEPROM memory
    # Second byte is addr MSB
    # Third byte is addr LSB
    # Fourth byte is data to write
    #
    AVR_WRT_EMEM_B1 = 0xC0


    #
    # Write memory page
    # Second byte is addr MSB
    # Third byte is addr LSB
    #
    AVR_WRT_EMEM_PAGE_B1 = 0xC2
    AVR_WRT_EMEM_PAGE_B4 = 0x00

    #
    # Write lock bits
    # Fourth byte is data
    #
    AVR_WRT_LCK_B1 = 0xAC
    AVR_WRT_LCK_B2	= 0xE0
    AVR_WRT_LCK_B3	= 0x00

    #
    # Write fuse bits(as I understand LOW)
    # fourth byte is data
    #
    AVR_WRT_LFUSE_B1 = 0xAC
    AVR_WRT_LFUSE_B2 = 0xA0
    AVR_WRT_LFUSE_B3 = 0x00

    #
    # Write high fuse bits
    # Fourth byte is data
    #
    AVR_WRT_HFUSE_B1 = 0xAC
    AVR_WRT_HFUSE_B2 = 0xA8
    AVR_WRT_HFUSE_B3 = 0x00

    #
    #	Write extended fuse bits
    #	Fourth byte is data
    #
    AVR_WRT_EXTFUSE_B1	= 0xAC
    AVR_WRT_EXTFUSE_B2	= 0xA4
    AVR_WRT_EXTFUSE_B3	= 0x00

    def __init__(self):
        return

# Masks to determine packet group
PL_CONTROL_PACKETS_MSK      =   0x10
PL_PROGRAMMER_PACKETS_MSK   =   0x20
PL_UART_PACKETS_MSG         =   0x40

# Control packets
PL_PROGRAMMER_INIT      =   0x10
PL_PROGRAMMER_STOP      =   0x11
PL_UART_INIT            =   0x12
PL_UART_STOP            =   0x13
PL_RESET                =   0x14
PL_ACK                  =   0x15
PL_CLOSE_CONNECTION     =   0x16
PL_NETWORK_CONFIG       =   0x17
PL_SET_OBSERVER_KEY     =   0x18
PL_SET_ENCRYPTION_KEYS  =   0x19
PL_SET_SIGN_KEYS        =   0x1A
PL_ENABLE_ENCRYPTION    =   0x1B
PL_ENABLE_SIGN          =   0x1C
PL_ERROR                =   0x1D

# Programmer packets
PL_LOAD_MCU_INFO        =   0x20
PL_PROGRAM_MEMORY       =   0x21
PL_READ_MEMORY          =   0x22
PL_MEMORY               =   0x23
PL_CMD                  =   0x24

# UART packets
PL_UART_CONFIGURATION   =   0x40
PL_UART_DATA            =   0x41

# Header structure
PL_START_FRAME_BYTE         =   0x1B

PL_FLAGS_FIELD_OFFSET          =   1
PL_FLAGS_FIELD_SIZE            =   1

PL_TYPE_FIELD_OFFSET	    =   PL_FLAGS_FIELD_SIZE + PL_FLAGS_FIELD_OFFSET
PL_TYPE_FIELD_SIZE		    =   1

PL_SIZE_FIELD_OFFSET	    =   PL_TYPE_FIELD_OFFSET + PL_TYPE_FIELD_SIZE
PL_SIZE_FIELD_SIZE		    =   2

PL_PACKET_HEADER_SIZE	    =   (1 + PL_SIZE_FIELD_SIZE + PL_TYPE_FIELD_SIZE +
                            PL_FLAGS_FIELD_SIZE)
PL_RESERVED_BYTES	    =   PL_PACKET_HEADER_SIZE

# Flags byte
PL_FLAG_COMPRESSION_BIT     =   0
PL_FLAG_ENCRYPTION_BIT      =   1
PL_FLAG_SIGN_BIT            =   2

# Maximum data field length
PL_MAX_DATA_LENGTH          = 1029

# Init programmer packet
PL_AVR_PROGRAMMER_BYTE      = 0x00

# ACK packet
PL_ACK_BYTE_OFFSET          =   0
PL_ACK_FAILURE              =   0
PL_ACK_SUCCESS              =   1

# Reset packet structure
PL_RESET_BYTE_OFFSET	    =   0
PL_RESET_ENABLE 	    =   1
PL_RESET_DISABLE	    =   0

# Set observer key
PL_OBSERVER_KEY_OFFSET      =   0
PL_SET_OBSERVER_KEY_SIZE    =   32

# Network packet
PL_NETWORK_MODE_OFFSET      =   0
PL_NETWORK_MODE_STA         =   0
PL_NETWORK_MODE_AP          =   1

PL_NETWORK_PHY_OFFSET       =   1
PL_NETWORK_PHY_B            =   0
PL_NETWORK_PHY_G            =   1
PL_NETWORK_PHY_N            =   2

PL_NETWORK_CHANNEL_OFFSET   =   2
PL_NETWORK_SSID_LEN_OFFSET  =   3

# USART Packet structure
PL_USART_BAUDRATE_OFFSET        =   0
PL_USART_PARITY_OFFSET    	=   (PL_USART_BAUDRATE_OFFSET+1)
PL_USART_DATA_BITS_OFFSET 	=   (PL_USART_PARITY_OFFSET+1)
PL_USART_STOP_BITS_OFFSET 	=   (PL_USART_DATA_BITS_OFFSET+1)

# USART Config bytes
PL_USART_PARITY_EVEN	    =   0xC0
PL_USART_PARITY_ODD	    =   0xC1
PL_USART_PARITY_NONE	    =   0xC2
PL_USART_DATA_BITS_8	    =   0xC3
PL_USART_DATA_BITS_9	    =   0xC4
PL_USART_STOP_BITS_1	    =   0xC5
PL_USART_STOP_BITS_2	    =   0xC6
PL_USART_BAUDRATE_9600      =   0xC7
PL_USART_BAUDRATE_19200	    =   0xC8
PL_USART_BAUDRATE_38400     =   0xC9
PL_USART_BAUDRATE_57600	    =   0xCA
PL_USART_BAUDRATE_74880     =   0xCB
PL_USART_BAUDRATE_115200    =   0xCC

# USART errors
USART_PARITY_ERROR_BYTE 	=   0xE0
USART_FRAME_ERROR_BYTE		=   0xE1
USART_DATA_BITS_ERROR_BYTE	=   0xE2
USART_STOP_BITS_ERROR_BYTE	=   0xE3
USART_BAUDRATE_ERROR_BYTE	=   0xE4

# 修正Makefile，添加必要的HAL库支持
makefile_fixed = '''
##########################################################################################################################
# STM32F407 Yaskawa Encoder Reader Makefile
##########################################################################################################################

######################################
# target
######################################
TARGET = yaskawa_encoder

######################################
# building variables
######################################
# debug build?
DEBUG = 1
# optimization
OPT = -Og

#######################################
# paths
#######################################
# Build path
BUILD_DIR = build

# HAL库路径 (需要用户下载STM32F4xx HAL库)
# 请将STM32Cube_FW_F4_V1.27.1下载到项目目录下，或修改此路径
HAL_PATH = STM32Cube_FW_F4_V1.27.1

######################################
# source
######################################
# C sources
C_SOURCES =  \\
main.c \\
yaskawa.c \\
stm32f4xx_it.c \\
system_stm32f4xx.c

# HAL源文件 (基本必需的)
ifneq ("$(wildcard $(HAL_PATH))","")
C_SOURCES += \\
$(HAL_PATH)/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal.c \\
$(HAL_PATH)/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_cortex.c \\
$(HAL_PATH)/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_dma.c \\
$(HAL_PATH)/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_flash.c \\
$(HAL_PATH)/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_flash_ex.c \\
$(HAL_PATH)/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_gpio.c \\
$(HAL_PATH)/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_pwr.c \\
$(HAL_PATH)/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_pwr_ex.c \\
$(HAL_PATH)/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_rcc.c \\
$(HAL_PATH)/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_rcc_ex.c \\
$(HAL_PATH)/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_tim.c \\
$(HAL_PATH)/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_tim_ex.c \\
$(HAL_PATH)/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_uart.c
endif

# ASM sources
ASM_SOURCES =  \\
startup_stm32f407xx.s

#######################################
# binaries
#######################################
PREFIX = arm-none-eabi-
ifdef GCC_PATH
CC = $(GCC_PATH)/$(PREFIX)gcc
AS = $(GCC_PATH)/$(PREFIX)gcc -x assembler-with-cpp
CP = $(GCC_PATH)/$(PREFIX)objcopy
SZ = $(GCC_PATH)/$(PREFIX)size
else
CC = $(PREFIX)gcc
AS = $(PREFIX)gcc -x assembler-with-cpp
CP = $(PREFIX)objcopy
SZ = $(PREFIX)size
endif
HEX = $(CP) -O ihex
BIN = $(CP) -O binary -S
 
#######################################
# CFLAGS
#######################################
# cpu
CPU = -mcpu=cortex-m4

# fpu
FPU = -mfpu=fpv4-sp-d16

# float-abi
FLOAT-ABI = -mfloat-abi=hard

# mcu
MCU = $(CPU) -mthumb $(FPU) $(FLOAT-ABI)

# macros for gcc
# AS defines
AS_DEFS = 

# C defines
C_DEFS =  \\
-DUSE_HAL_DRIVER \\
-DSTM32F407xx

# AS includes
AS_INCLUDES = 

# C includes
C_INCLUDES =  \\
-I.

# 如果HAL库存在，添加HAL头文件路径
ifneq ("$(wildcard $(HAL_PATH))","")
C_INCLUDES += \\
-I$(HAL_PATH)/Drivers/STM32F4xx_HAL_Driver/Inc \\
-I$(HAL_PATH)/Drivers/STM32F4xx_HAL_Driver/Inc/Legacy \\
-I$(HAL_PATH)/Drivers/CMSIS/Device/ST/STM32F4xx/Include \\
-I$(HAL_PATH)/Drivers/CMSIS/Include
endif

# compile gcc flags
ASFLAGS = $(MCU) $(AS_DEFS) $(AS_INCLUDES) $(OPT) -Wall -fdata-sections -ffunction-sections

CFLAGS = $(MCU) $(C_DEFS) $(C_INCLUDES) $(OPT) -Wall -fdata-sections -ffunction-sections

ifeq ($(DEBUG), 1)
CFLAGS += -g -gdwarf-2
endif

# Generate dependency information
CFLAGS += -MMD -MP -MF"$(@:%.o=%.d)"

#######################################
# LDFLAGS
#######################################
# link script
LDSCRIPT = STM32F407VGTx_FLASH.ld

# libraries
LIBS = -lc -lm -lnosys 
LIBDIR = 
LDFLAGS = $(MCU) -specs=nano.libs -T$(LDSCRIPT) $(LIBDIR) $(LIBS) -Wl,-Map=$(BUILD_DIR)/$(TARGET).map,--cref -Wl,--gc-sections

# default action: build all
all: $(BUILD_DIR)/$(TARGET).elf $(BUILD_DIR)/$(TARGET).hex $(BUILD_DIR)/$(TARGET).bin

#######################################
# build the application
#######################################
# list of objects
OBJECTS = $(addprefix $(BUILD_DIR)/,$(notdir $(C_SOURCES:.c=.o)))
vpath %.c $(sort $(dir $(C_SOURCES)))
# list of ASM program objects
OBJECTS += $(addprefix $(BUILD_DIR)/,$(notdir $(ASM_SOURCES:.s=.o)))
vpath %.s $(sort $(dir $(ASM_SOURCES)))

$(BUILD_DIR)/%.o: %.c Makefile | $(BUILD_DIR) 
	$(CC) -c $(CFLAGS) -Wa,-a,-ad,-alms=$(BUILD_DIR)/$(notdir $(<:.c=.lst)) $< -o $@

$(BUILD_DIR)/%.o: %.s Makefile | $(BUILD_DIR)
	$(AS) -c $(CFLAGS) $< -o $@

$(BUILD_DIR)/$(TARGET).elf: $(OBJECTS) Makefile
	$(CC) $(OBJECTS) $(LDFLAGS) -o $@
	$(SZ) $@

$(BUILD_DIR)/%.hex: $(BUILD_DIR)/%.elf | $(BUILD_DIR)
	$(HEX) $< $@
	
$(BUILD_DIR)/%.bin: $(BUILD_DIR)/%.elf | $(BUILD_DIR)
	$(BIN) $< $@	
	
$(BUILD_DIR):
	mkdir $@		

#######################################
# clean up
#######################################
clean:
	-rm -fR $(BUILD_DIR)

#######################################
# help
#######################################
help:
	@echo "Available targets:"
	@echo "  all       - Build the project"
	@echo "  clean     - Clean build files"
	@echo "  flash     - Flash using st-flash"
	@echo "  openocd-flash - Flash using OpenOCD"
	@echo "  debug     - Start GDB debug session"
	@echo ""
	@echo "Requirements:"
	@echo "  1. ARM GCC toolchain (arm-none-eabi-gcc)"
	@echo "  2. STM32F4xx HAL library (optional, for full functionality)"
	@echo "  3. st-flash or OpenOCD for flashing"
  
#######################################
# flash
#######################################
flash: $(BUILD_DIR)/$(TARGET).bin
	st-flash write $< 0x8000000

#######################################
# openocd flash
#######################################
openocd-flash: $(BUILD_DIR)/$(TARGET).bin
	openocd -f interface/stlink-v2.cfg -f target/stm32f4x.cfg -c "program $< 0x8000000 verify reset exit"

#######################################
# debug with gdb
#######################################
debug: $(BUILD_DIR)/$(TARGET).elf
	arm-none-eabi-gdb -x gdb_init $<

#######################################
# simple build (without HAL library)
#######################################
simple: C_SOURCES = main.c yaskawa.c stm32f4xx_it.c system_stm32f4xx.c
simple: $(BUILD_DIR)/$(TARGET).elf $(BUILD_DIR)/$(TARGET).hex $(BUILD_DIR)/$(TARGET).bin
	@echo "Simple build completed (without HAL library)"
	@echo "Note: Some functionality may be limited"

#######################################
# dependencies
#######################################
-include $(wildcard $(BUILD_DIR)/*.d)

.PHONY: all clean flash openocd-flash debug help simple

# *** EOF ***
'''

with open("Makefile", "w") as f:
    f.write(makefile_fixed)

print("Makefile已修正并添加HAL库支持")
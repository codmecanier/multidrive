#include <sys/stat.h>
#include <stdlib.h>
#include <errno.h>
#include <stdio.h>
#include "usart.h"

// 系统调用重定向
int _write(int file, char *ptr, int len)
{
    int i;
    for (i = 0; i < len; i++)
    {
        while((USART1->SR & 0X40) == 0); // 等待 TXE
        USART1->DR = (uint8_t)ptr[i];
    }
    return len;
}

int _read(int file, char *ptr, int len)
{
    // 如果需要从串口读取，可以在这里实现
    return 0;
}

int _close(int file)
{
    return -1;
}

int _lseek(int file, int ptr, int dir)
{
    return 0;
}

int _fstat(int file, struct stat *st)
{
    st->st_mode = S_IFCHR;
    return 0;
}

int _isatty(int file)
{
    return 1;
}

void _exit(int status)
{
    while(1);
}

void _kill(int pid, int sig)
{
    return;
}

int _getpid(void)
{
    return 1;
}
import crcmod

class CRCUtil:
    crc16_func = crcmod.mkCrcFun(
        0x18005,
        rev=True,
        initCrc=0xFFFF,
        xorOut=0x0000
    )

    @staticmethod
    def crc16(data: str) -> str:
        return f"{CRCUtil.crc16_func(data.encode('utf-8')):04X}"

    @staticmethod
    def lrc(data: str) -> str:
        total = 0

        start_idx = data.find('#')
        end_idx = data.find('*')

        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            for char in data[start_idx:end_idx + 1]:
                total += ord(char)

        checksum = total % 256
        return f"{checksum:02X}"
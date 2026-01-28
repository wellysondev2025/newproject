import re

def validar_cpf(cpf: str) -> str:
    """
    Valida o CPF e retorna apenas os números limpos.
    Lança ValueError se for inválido.
    """
    if not cpf:
        raise ValueError("CPF é obrigatório.")

    cpf_numbers = re.sub(r'\D', '', cpf)

    if len(cpf_numbers) != 11:
        raise ValueError("CPF deve ter 11 números.")

    if cpf_numbers in [c*11 for c in "0123456789"]:
        raise ValueError("CPF inválido.")

    def calc_dv(digs):
        s = sum(int(d) * w for d, w in zip(digs, range(len(digs)+1, 1, -1)))
        r = 11 - s % 11
        return '0' if r >= 10 else str(r)

    dv1 = calc_dv(cpf_numbers[:9])
    dv2 = calc_dv(cpf_numbers[:9] + dv1)

    if cpf_numbers[-2:] != dv1 + dv2:
        raise ValueError("CPF inválido.")

    return cpf_numbers

# -*- coding: utf-8 -*-
"""
Codificação temática das respostas abertas por palavras-chave.

Cada tema tem uma lista de padrões (expressões regulares aplicadas ao texto
em minúsculas e sem acento). Uma resposta pode receber mais de um tema.
`exceto` evita dupla contagem entre temas sobrepostos: se algum dos temas
listados já foi atribuído, este é ignorado. Resposta sem nenhum tema cai em
"Outros".

A codificação é determinística e auditável: para ajustar, edite os padrões.
"""
import re
import unicodedata


def _norm(t):
    t = unicodedata.normalize('NFKD', str(t)).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'\s+', ' ', t)


TEMAS_BENEFICIO = [
    ('Atendimento próximo e resolutivo', [r'(?<!rede de )atendimento', r'suporte', r'gerente', r'contato com (o )?time',
                                         r'resolutiv', r'whatsapp', r'enfermeir', r'\bcs\b'], []),
    ('Rede credenciada', [r'\brede\b', r'hospita', r'laboratori', r'clinicas', r'opcoes de onde ir'], []),
    ('App e tecnologia', [r'\bapp\b', r'aplicativo', r'digital', r'online'], []),
    ('Modelo de cuidado', [r'medic[oa] (da |de )?familia', r'plantao digital', r'compartilhadas entre os medicos',
                           r'centraliz'], []),
    ('Qualidade do corpo médico', [r'corpo medico', r'equipe medica', r'qualidade dos medicos', r'medicos da base',
                                   r'profissionais qualificados', r'atendimento dos profissionais'], []),
    ('Tranquilidade e acesso à saúde', [r'seguranca', r'conforto', r'tranquil', r'mais saude', r'saude do', r'atendimento de saude',
                                        r'em qualquer lugar'], []),
    ('Custo-benefício', [r'custo'], []),
    ('Gestão simples para o RH', [r'burocracia', r'manutencao', r'inclusao', r'exclusao', r'facilidade de manusear',
                                  r'profissionais pj', r'agendamento'], []),
    ('Prevenção e campanhas', [r'preven', r'campanha'], []),
    ('Humanização', [r'human', r'acolh', r'intencao de ajudar', r'personalizado'], []),
    ('Qualidade geral percebida', [r'qualidade do servico', r'melhor convenio', r'superior aos outros', r'como um todo',
                                   r'locais de qualidade', r'hospitais com qualidade'], []),
    ('Experiência do colaborador', [r'experiencia', r'colaboradores amam', r'retencao', r'atracao de talentos'], []),
]

TEMAS_MELHORAR = [
    ('Ampliar rede fora de SP e no interior', [r'fora de (sao paulo|sp)', r'interior', r'outros estados', r'municipios',
                                              r'mais regioes'], []),
    ('Ampliar rede — hospitais e laboratórios', [r'hospita', r'laboratori', r'rede credenciada', r'\brede\b', r'coberturas'],
     ['Ampliar rede fora de SP e no interior']),
    ('Coparticipação, preço e transparência', [r'copart', r'co-participa', r'preco', r'valores', r'sinistralidade'], []),
    ('Relatórios e visibilidade de uso', [r'relatorio', r'report', r'\bvisibilidade', r'dashb', r'grafico'], []),
    ('Campanhas e ações de prevenção', [r'campanha', r'palestra', r'preven'], []),
    ('Processos administrativos e documentação', [r'fatura', r'documenta', r'administrativ'], []),
    ('Agilidade em autorizações', [r'libera', r'liveracao', r'autoriza', r'retornos de cobertura'], []),
    ('Clareza de processos e comunicação', [r'confus', r'deixar mais claro', r'comunicacao'], []),
    ('Usabilidade do app e acesso a dados', [r'\bapp\b', r'aplicativo', r'meus dados', r'smartwatch', r'novas tecnologias'], []),
    ('Agendamento e disponibilidade de agenda', [r'agenda'], ['Ampliar rede fora de SP e no interior']),
    ('Nada a melhorar / já satisfeito', [r'nao tenho nada', r'nada a (opinar|declarar|acrescentar|sugerir)',
                                         r'nada de relevante', r'esta otimo', r'esta tudo', r'tudo muito bom',
                                         r'satisfeit', r'nao tenho reclama'], ['*']),
    ('Outros', [r'odonto'], []),
]

CLASSES_ATENDIMENTO = [
    ('Com ressalva ou sugestão', 'amber', [r'apreensiv', r'poderia', r'sugiro', r'sugest', r'demor', r'\bporem\b',
                                           r'deveria', r'falta']),
    ('Elogio explícito ao CSM', 'green', [r'excelente', r'otim', r'atencios', r'incrivel', r'perfeit', r'obrigad',
                                          r'gratidao', r'solicit', r'sempre resolve', r'contente', r'facilita',
                                          r'manter a qualidade', r'proximidade', r'super bem', r'acolhid',
                                          r'satisfeit', r'muito bem']),
]
SEM_APONTAMENTO = ('Sem apontamento', 'grey')


def codificar(texto, temas):
    """Lista de temas atribuídos a um texto ('*' em exceto = só se nenhum outro tema)."""
    t = _norm(texto)
    achados = []
    for nome, padroes, exceto in temas:
        if not any(re.search(p, t) for p in padroes):
            continue
        if '*' in exceto and any(a != 'Outros' for a in achados):
            continue
        if any(e in achados for e in exceto if e != '*'):
            continue
        achados.append(nome)
    # "nada a melhorar" é exclusivo: se aparecer junto de outro tema, prevalece o outro
    if len(achados) > 1 and 'Nada a melhorar / já satisfeito' in achados:
        achados.remove('Nada a melhorar / já satisfeito')
    return achados or ['Outros']


def classificar_atendimento(texto):
    """(rótulo, tipo_de_badge) para a resposta sobre o atendimento do gerente."""
    t = _norm(texto)
    for rotulo, tipo, padroes in CLASSES_ATENDIMENTO:
        if any(re.search(p, t) for p in padroes):
            return rotulo, tipo
    return SEM_APONTAMENTO

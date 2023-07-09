from django.shortcuts import render
from django.shortcuts import redirect
from contas.models import ContaPaga, ContaPagar
from perfil.models import Categoria
from django.contrib.messages import constants
from django.contrib import messages
from datetime import datetime

def definir_contas(request):
    if request.method == 'GET':
        categorias = Categoria.objects.all()
        return render(request, 'definir_contas.html', {'categorias': categorias})
    elif request.method == 'POST':
        titulo = request.POST.get('titulo')
        categoria = request.POST.get('categoria')
        descricao = request.POST.get('descricao')
        valor = request.POST.get('valor')
        dia_pagamento = request.POST.get('dia_pagamento')

        conta = ContaPagar(
            titulo = titulo,
            categoria_id = categoria,
            descricao = descricao,
            valor = valor,
            dia_pagamento = dia_pagamento,
        )

        conta.save()

        messages.add_message(request, constants.SUCCESS, 'Conta cadastrada com sucesso.')
        return redirect('/contas/definir_contas')
    
def ver_contas(request):
    MES_ATUAL = datetime.now().month
    DIA_ATUAL = datetime.now().day
    
    contas = ContaPagar.objects.all()

    contas_pagas = ContaPaga.objects.filter(data_pagamento__month=MES_ATUAL).values('conta')

    contas_vencidas = contas.filter(dia_pagamento__lt=DIA_ATUAL).exclude(id__in=contas_pagas)
    quantidade_contas_vencidas = contas_vencidas.count()
    
    contas_proximas_vencimento = contas.filter(dia_pagamento__lte = DIA_ATUAL + 5).filter(dia_pagamento__gte=DIA_ATUAL).exclude(id__in=contas_pagas)
    quantidade_contas_proximas_vencimento = contas_proximas_vencimento.count()
    
    restantes = contas.exclude(id__in=contas_vencidas).exclude(id__in=contas_pagas).exclude(id__in=contas_proximas_vencimento)

    return render(request, 'ver_contas.html', {'contas_vencidas': contas_vencidas, 'contas_proximas_vencimento': contas_proximas_vencimento, 'restantes': restantes, 'quantidade_contas_proximas_vencimento': quantidade_contas_proximas_vencimento, 'quantidade_contas_vencidas': quantidade_contas_vencidas})
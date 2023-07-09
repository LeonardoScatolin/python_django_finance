from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.messages import constants
from django.http import HttpResponse

from contas.models import ContaPaga, ContaPagar
from .utils import calcula_total
from .utils import calcula_equilibrio_financeiro
from django.db.models import Sum

from extrato.models import Valores
from .models import Conta
from .models import Categoria
from datetime import datetime


def home(request):
    valores = Valores.objects.filter(data__month = datetime.now().month)
    entradas = valores.filter(tipo='E')
    saidas = valores.filter(tipo='S')

    total_entradas = calcula_total(entradas, 'valor')
    total_saidas = calcula_total(saidas, 'valor')

    contas = Conta.objects.all()

    total_contas = 0
    for conta in contas:
        total_contas += conta.valor

    percentual_gastos_essenciais, percentual_gastos_nao_essenciais = calcula_equilibrio_financeiro()

    DIA_ATUAL = datetime.now().day
    MES_ATUAL = datetime.now().month
    contaPagar = ContaPagar.objects.all()
    contas_pagas = ContaPaga.objects.filter(data_pagamento__month=MES_ATUAL).values('conta')

    contas_vencidas = contaPagar.filter(dia_pagamento__lt=DIA_ATUAL).exclude(id__in=contas_pagas)
    quantidade_contas_vencidas = contas_vencidas.count()

    contas_proximas_vencimento = contaPagar.filter(dia_pagamento__lte = DIA_ATUAL + 5).filter(dia_pagamento__gte=DIA_ATUAL).exclude(id__in=contas_pagas)
    quantidade_contas_proximas_vencimento = contas_proximas_vencimento.count()
    
    return render(request, 'home.html', {'contas': contas, 'total_contas': total_contas, 'total_entradas':total_entradas, 'total_saidas':total_saidas, 'percentual_gastos_essenciais':int(percentual_gastos_essenciais), 'percentual_gastos_nao_essenciais':int(percentual_gastos_nao_essenciais), 'quantidade_contas_proximas_vencimento': quantidade_contas_proximas_vencimento, 'quantidade_contas_vencidas': quantidade_contas_vencidas})

def gerenciar(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()
    total_contas = 0
    for conta in contas:
        total_contas += conta.valor

    bancos = Conta.banco_choices
    tipos_conta = Conta.tipo_choices
    
    return render(request, 'gerenciar.html', {'contas': contas, 'total_contas': total_contas, 'categorias': categorias, 'bancos': bancos, 'tipos_conta': tipos_conta})

def cadastrar_banco(request):
    apelido = request.POST.get('apelido')
    banco = request.POST.get('banco')
    tipo = request.POST.get('tipo')
    valor = request.POST.get('valor')
    icone = request.FILES.get('icone')

    if len(apelido.strip()) == 0 or len(valor.strip()) == 0 or len(banco.strip()) == 0:
        messages.add_message(request, constants.ERROR, 'Preencha todos os campos.')
        return redirect('/perfil/gerenciar')

    conta = Conta(
        apelido = apelido,
        banco = banco,
        tipo = tipo,
        valor = valor,
        icone = icone
    )
    conta.save()
    
    messages.add_message(request, constants.SUCCESS, 'Conta cadastrada com sucesso.')
    return redirect('/perfil/gerenciar')

def deletar_banco(request, id):
    conta = Conta.objects.get(id=id)
    conta.delete()

    messages.add_message(request, constants.SUCCESS, 'Conta deletada com sucesso.')
    return redirect('/perfil/gerenciar')

def cadastrar_categoria(request):
    nome = request.POST.get('categoria')
    essencial = bool(request.POST.get('essencial'))

    if len(nome.strip()) == 0:
        messages.add_message(request, constants.ERROR, 'Categoria não pode ser vazio.')
        return redirect('/perfil/gerenciar')
    
    categoria = Categoria(
        categoria=nome,
        essencial=essencial
    )
    categoria.save()

    messages.add_message(request, constants.SUCCESS, 'Categoria cadastrada com sucesso')
    return redirect('/perfil/gerenciar/')

def update_categoria(request, id):
    categoria = Categoria.objects.get(id=id)
    categoria.essencial = not categoria.essencial
    categoria.save()

    return redirect('/perfil/gerenciar/')

def dashboard(request):
    dados = {}
    categorias = Categoria.objects.all()

    for categoria in categorias:
        total = 0
        valores =Valores.objects.filter(categoria=categoria)
        for v in valores:
            total = total + v.valor

        dados[categoria.categoria] = total


    return render(request, 'dashboard.html', {'labels': list(dados.keys()), 'values': list(dados.values())})

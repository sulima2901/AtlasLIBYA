from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from .models import Offer
from .forms import OfferForm

class OfferCreateView(CreateView):
    model = Offer
    form_class = OfferForm
    template_name = 'offers/offer_form.html'
    success_url = reverse_lazy('offers:offers_list')

class OfferListView(ListView):
    model = Offer
    template_name = 'offers/offers_list.html'
    context_object_name = 'offers'

def offers_list(request):
    offers = Offer.objects.all()
    return render(request, 'offers/offers_list.html', {'offers': offers})
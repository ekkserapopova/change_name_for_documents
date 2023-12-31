from django.shortcuts import render, redirect

docs = [
            {'title': 'Паспорт РФ', 'name': 'pasport', 'overview': 'Основной документ, удостоверяющий личность, внутренний паспорт гражданина России на территории РФ.', 'description': '''     Срок предоставления услуги: 30 дней
             
                  Для предоставления услуги по замене фамилии в паспорте РФ следует заполнить заявку по смене фамилии:
                    - указать Ваши данные (ФИО, номер+серия паспорта, кем выдан, дата выдачи, регистрация)
                    - указать фамилию, на которую вы хотите заменить свою нынешнюю
                    - указать причину, по которой вы зотите сменить фамилию

                    В течение установленного срока после подачи заявления Вам будет вынесено решение по заявке.
                    
                    Стоимость услуги 3500руб.
''', 'image': 'static/passport_rf.jpg'},
            {'title': 'Загранпаспорт', 'name': 'zagranpasport', 'overview': 'Официальный документ, удостоверяющий личность гражданина при выезде за пределы и пребывании за пределами государства, а также при въезде на территорию государства из заграничной поездки.','description': '''Срок предоставления услуги: 3 месяца
             Для предоставления услуги по замене фамилии в загранпаспорте следует заполнить заявку по смене фамилии:
                - указать Ваши данные (ФИО, номер+серия паспорта, кем выдан, дата выдачи, регистрация)
                - указать номер загранпаспорта
                - указать фамилию, на которую вы хотите заменить свою нынешнюю
                - указать причину, по которой вы зотите сменить фамилию

                В течение установленного срока после подачи заявления Вам будет вынесено решение по заявке.
                
                Стоимость услуги 2000-5000руб.''', 'image': 'static/zagran.jpeg'},
            {'title': 'Свидетельство о рождении', 'name': 'birthcertificate', 'overview': 'Свидетельство о государственной регистрации акта гражданского состояния — факта рождения человека.','description': '''Срок предоставления услуги: от 1 до 3 месяцев
             Для предоставления услуги по замене фамилии в свидетельстве о рождении следует заполнить заявку по смене фамилии:
                - указать Ваши данные (ФИО, номер+серия паспорта, кем выдан, дата выдачи, регистрация)
                - указать номер свидетельства о рождении
                - указать фамилию, на которую вы хотите заменить свою нынешнюю
                - указать причину, по которой вы зотите сменить фамилию

                В течение установленного срока после подачи заявления Вам будет вынесено решение по заявке.
                
                Стоимость услуги 2000руб.''', 'image': 'static/birth_sertificate.jpg'},
            {'title': 'Свидетельство о заключении брака', 'name': 'merriagecertificate', 'overview': 'Официальный документ, подтверждающий, что два человека состоят в браке.','description': '''Срок предоставления услуги: от 1 до 2 месяцев
             Для предоставления услуги по замене фамилии в свидетельстве о заключении брака следует заполнить заявку по смене фамилии:
                - указать Ваши данные (ФИО, номер+серия паспорта, кем выдан, дата выдачи, регистрация)
                - указать номер свидетельства о заключении брака
                - указать фамилию, на которую вы хотите заменить свою нынешнюю
                - указать причину, по которой вы зотите сменить фамилию

                В течение установленного срока после подачи заявления Вам будет вынесено решение по заявке.
                
                Стоимость услуги 2000руб.''', 'image': 'static/merriage_sertificate.jpeg'},
        ]

    
# def GetDocuments(request):
#     return render(request, 'documents.html', {'data' : {
#         'docs': docs
#     }})
    
def GetDocument(request, name):
    for doc in docs:
        if doc['name'] == name:
            title = doc['title']
            description = doc['description']
            image = doc['image']
            break
    return render(request, 'document.html', {'data' : {
        'name': name,
        'title': title,
        'description': description,
        'image': image,
}})
    
def search(request):
    inputValue = request.GET.get('search_query') 
    query = inputValue
    if query:  
        filtered_items = [doc for doc in docs if query.lower() in doc['title'].lower() ]  
    else:
        filtered_items = docs  

    return render(request, 'documents.html', {'items': filtered_items,})

# Create your views here.

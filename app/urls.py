from django.urls import path

from .views import( 
    register_user, 
    login_user, 
    change_password, 
    ticket_list_create,
    transactions_view, 
    get_user_profile,
    upload_kyc,
    withdrawal_view,
    transaction_history,
    payment_methods,
    get_deposit_options,
    create_deposit,
    
    

)

urlpatterns = [
    path("register/", register_user, name="register"),
    path("login/", login_user, name="login"),
    path("profile/", get_user_profile, name="get_user_profile"),
    path("tickets/", ticket_list_create, name="tickets_view"),
    path("transactions/", transactions_view, name="transactions_view"),

     path("change-password/", change_password, name="change-password"),
     path("withdrawal/", withdrawal_view, name="withdrawal"),

     path("kyc/upload/", upload_kyc, name="upload_kyc"),
     path("transactions/", transaction_history, name="transaction-history"),
     path("payments/", payment_methods, name="payments"),
     
     path("admin-wallets/", get_deposit_options, name="get_deposit_options"),

     path("deposits/", create_deposit, name="create-deposit"),

]


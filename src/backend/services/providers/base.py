from abc import ABC, abstractmethod


class BasePaymentProvider(ABC):
    @abstractmethod
    def get_access_token(self):
        raise NotImplementedError

    @abstractmethod
    def create_virtual_account(self, account_ref, account_name, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get_virtual_account(self, account_id):
        raise NotImplementedError

    @abstractmethod
    def transfer_to_bank(self, bank_code, account_number, amount, narration, reference):
        raise NotImplementedError

    @abstractmethod
    def verify_bank_account(self, bank_code, account_number):
        raise NotImplementedError

    @abstractmethod
    def get_banks(self):
        raise NotImplementedError

    @abstractmethod
    def create_direct_debit_mandate(
        self, customer_data, amount, frequency, start_date, end_date
    ):
        raise NotImplementedError

    @abstractmethod
    def charge_tokenized_card(self, token_key, amount, reference, customer_id):
        raise NotImplementedError

    @abstractmethod
    def get_transaction(self, transaction_ref):
        raise NotImplementedError

    @abstractmethod
    def verify_webhook(self, payload, signature):
        raise NotImplementedError

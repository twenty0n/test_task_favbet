from abc import ABC, abstractmethod


class Repository(ABC):

    @abstractmethod
    def save(self, data: list):
        """
        Save data to repository
        :param data: list with data for save
        :return: None
        """
        pass

    @abstractmethod
    def get(self, *, _filter: str, limit: int, offset: int):
        """
        Getting data from db
        :param limit: limit for data
        :param offset: offset when receiving data
        :param _filter:
        :return:
        """
        pass

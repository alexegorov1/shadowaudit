from abc import ABC, abstractmethod

class BaseCollector(ABC):
    @abstractmethod
    def collect(self):
        pass

class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, data):
        pass

class BaseReporter(ABC):
    @abstractmethod
    def generate_report(self, results):
        pass

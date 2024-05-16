import logging
from pydantic import BaseModel
from typing import Optional, Dict

import utils.constants as constants


class ModelConfig(BaseModel):
    name: str = None
    url: str = None
    credential_path: str = None
    credentials: str = None

    def __init__(self, data: dict = None):
        super().__init__()
        if data is None:
            return
        self.name = data.get("name", None)
        self.url = data.get("url", None)
        self.credential_path = data.get("credential_path", None)


class ProviderConfig(BaseModel):
    name: str = None
    url: str = None
    credential_path: str = None
    credentials: str = None
    models: Dict[str, ModelConfig] = {}

    def __init__(self, data: dict = None):
        super().__init__()
        if data is None:
            return
        self.name = data.get("name", None)
        self.url = data.get("url", None)
        self.credential_path = data.get("credential_path", None)
        if data.get("models", None) is None or len(data["models"]) == 0:
            raise Exception(f"no models configured for provider {data['name']}")
        for m in data["models"]:
            if m.get("name", None) is None:
                raise Exception("model name is missing")
            model = ModelConfig(m)
            self.models[m["name"]] = model


class LLMConfig(BaseModel):
    providers: Dict[str, ProviderConfig] = {}

    def __init__(self, data: dict = None):
        super().__init__()
        if data is None:
            return
        for p in data:
            if p.get("name", None) is None:
                raise Exception("provider name is missing")
            provider = ProviderConfig(p)
            self.providers[p["name"]] = provider


class RedisConfig(BaseModel):
    host: str = None
    port: int = None
    max_memory: str = None
    max_memory_policy: str = None

    def __init__(self, data: dict = None):
        super().__init__()
        if data is None:
            return
        self.host = data.get("host", None)
        self.port = data.get("port", None)
        self.max_memory = data.get("max_memory", constants.REDIS_CACHE_MAX_MEMORY)
        self.max_memory_policy = data.get(
            "max_memory_policy", constants.REDIS_CACHE_MAX_MEMORY_POLICY
        )


class MemoryConfig(BaseModel):
    max_entries: int = None

    def __init__(self, data: dict = None):
        super().__init__()
        if data is None:
            return
        self.max_entries = data.get(
            "max_entries", constants.IN_MEMORY_CACHE_MAX_ENTRIES
        )


class ConversationCacheConfig(BaseModel):
    type: str = None
    redis: Optional[RedisConfig] = None
    memory: Optional[MemoryConfig] = None

    def __init__(self, data: dict = None):
        super().__init__()
        if data is None:
            return
        self.type = data.get("type", None)
        if self.type == "redis":
            if data.get("redis", None) is None:
                raise Exception("redis config is missing")
            self.redis = RedisConfig(data.get("redis", None))
        elif self.type == "in-memory":
            if data.get("in-memory", None) is None:
                raise Exception("in-memory config is missing")
            self.memory = MemoryConfig(data.get("memory", None))


class LoggerConfig(BaseModel):
    default_level: int = None
    default_filename: str = None
    default_size: int = None

    def __init__(self, data: dict = None):
        super().__init__()
        if data is None:
            return
        level = logging.getLevelName(data.get("default_level", "INFO"))
        if level is None:
            raise Exception(
                f"invalid log level for default log: {data.get('default_level',None)}"
            )
        self.default_level = level
        self.default_filename = data.get("default_filename", None)
        self.default_size = data.get("default_size", (1048576 * 100))


class OLSConfig(BaseModel):
    conversation_cache: ConversationCacheConfig = None
    logger_config: LoggerConfig = None

    enable_debug_ui: bool = False
    default_model: str = None
    default_provider: str = None

    classifier_provider: str = None
    classifier_model: str = None
    happy_response_provider: str = None
    happy_response_model: str = None
    summarizer_provider: str = None
    summarizer_model: str = None
    validator_provider: str = None
    validator_model: str = None
    yaml_provider: str = None
    yaml_model: str = None

    def __init__(self, data: dict = None):
        super().__init__()
        if data is None:
            return
        self.default_provider = data.get("default_provider", None)
        self.default_model = data.get("default_model", None)
        self.classifier_provider = data.get(
            "classifier_provider", self.default_provider
        )
        self.classifier_model = data.get("classifier_model", self.default_model)
        self.happy_response_model = data.get("happy_response_model", self.default_model)
        self.happy_response_provider = data.get(
            "happy_response_provider", self.default_provider
        )
        self.summarizer_provider = data.get(
            "summarizer_provider", self.default_provider
        )
        self.summarizer_model = data.get("summarizer_model", self.default_model)
        self.validator_provider = data.get("validator_provider", self.default_provider)
        self.validator_model = data.get("validator_model", self.default_model)
        self.yaml_provider = data.get("yaml_provider", self.default_provider)
        self.yaml_model = data.get("yaml_model", self.default_model)

        self.enable_debug_ui = data.get("enable_debug_ui", False)
        self.conversation_cache = ConversationCacheConfig(
            data.get("conversation_cache", None)
        )
        self.logger_config = LoggerConfig(data.get("logger_config", None))


class Config:
    llm_config: LLMConfig = None
    ols_config: OLSConfig = None

    def __init__(self, data: dict = None):
        super().__init__()
        if data is None:
            return
        self.llm_config = LLMConfig(data.get("llm_providers", None))
        self.ols_config = OLSConfig(data.get("ols_config", None))

    def validate(self):
        if self.llm_config is None:
            raise Exception("no llm config found")
        if self.llm_config.providers is None or len(self.llm_config.providers) == 0:
            raise Exception("no llm providers found")
        if self.ols_config is None:
            raise Exception("no ols config found")
        if self.ols_config.default_model is None:
            raise Exception("default model is not set")
        if self.ols_config.classifier_model is None:
            raise Exception("classifier model is not set")
        if self.ols_config.conversation_cache is None:
            raise Exception("conversation cache is not set")
        if self.ols_config.logger_config is None:
            raise Exception("logger config is not set")

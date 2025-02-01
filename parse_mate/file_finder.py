""" Buscador de arquivos

Módulo focado em buscar arquivos nos diretórios selecionados
"""

import os
import fnmatch

from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Union, List


class FilterType(Enum):
    GREATER_THAN = ">"
    GREATER_THAN_EQUAL = ">="
    EQUAL = "="
    LESS_THAN_EQUAL = "<="
    LESS_THAN = "<"


class OrderBy(Enum):
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"
    MODIFIED_ASC = "modified_asc"
    MODIFIED_DESC = "modified_desc"


_FILTER_OPERATORS = {
    FilterType.GREATER_THAN: lambda file_mod_time, filter_date: file_mod_time > filter_date,
    FilterType.GREATER_THAN_EQUAL: lambda file_mod_time, filter_date: file_mod_time >= filter_date,
    FilterType.EQUAL: lambda file_mod_time, filter_date: file_mod_time == filter_date,
    FilterType.LESS_THAN_EQUAL: lambda file_mod_time, filter_date: file_mod_time <= filter_date,
    FilterType.LESS_THAN: lambda file_mod_time, filter_date: file_mod_time < filter_date,
}

_ORDER_OPERATIONS = {
    OrderBy.NAME_ASC: lambda files: sorted(files, key=lambda x: str(x).lower()),
    OrderBy.NAME_DESC: lambda files: sorted(files, key=lambda x: str(x).lower(), reverse=True),
    OrderBy.MODIFIED_ASC: lambda files: sorted(files, key=lambda x: os.path.getmtime(str(x))),
    OrderBy.MODIFIED_DESC: lambda files: sorted(files, key=lambda x: os.path.getmtime(str(x)), reverse=True),
}


class FileFinder:
    """
    Classe responsável por buscar, filtrar e também ordenar os arquivos encontrados.

    Args:
        directory: Diretório de busca
        filename_pattern: padrão ou nome completo do arquivo
    
    Raises:
        FileNotFoundError: Quando o arquivo ou diretório não for encontrado
        NotADirectoryError: Quando o diretório não for encontrado
    """

    def __init__(self, directory: Union[str, Path], filename_pattern: str):
        self.directory = Path(directory) if not isinstance(directory, Path) else directory
        self.filename_pattern = filename_pattern

        if not os.path.exists(self.directory):
            raise FileNotFoundError(f"Diretório não encontrado: {self.directory.__str__}")
        if not os.path.isdir(self.directory):
            raise NotADirectoryError(f"{self.directory.__str__} não é um diretório válido")
        
    def find_files(self) -> List[Union[str, Path]]:
        """
        Econtra os arquivos desejados no diretório de busca

        Returns:
            Uma lista com os arquivos encontrados
        """

        matched_files = []

        for root, _, files in os.walk(self.directory):
            for file in files:
                if fnmatch.fnmatch(file, self.filename_pattern):
                    matched_files.append(os.path.join(root, file))
        return matched_files
    
    def filter_by_date(
            list_of_files: List[Union[str, Path]],
            filter_date: Union[date, datetime], 
            filter_type: FilterType = FilterType.EQUAL
        ) -> List[Union[str, Path]]:
        """
        Filtra os arquivos pela data de modificação com base no tipo de filtro.

        Args:
            list_of_files: Lista de arquivos (caminho completo)
            filter_date: Data base de filtragem do arquivo
            filter_type: Tipo de filtragem
        
        Returns:
            Lista de arquivos filtrados
        """
        filtered_files = []

        for file_path in list_of_files:
            file_path_str = str(file_path) if isinstance(file_path, Path) else file_path
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path_str))

            if _FILTER_OPERATORS[filter_type](file_mod_time, filter_date):
                filtered_files.append(file_path)

        return filtered_files

    def order_files(
        list_of_files: List[Union[str, Path]],
        order_by: OrderBy = OrderBy.MODIFIED_DESC
    ) -> List[str]:
        """
        Ordena os arquivos com base no tipo de ordenação especificado.

        Args:
            list_of_files: Lista de arquivos (caminho completo)
            order_by: Critério de ordenação (nome ou data de modificação)
        
        Raises:
            FileExistsError: Caso algum arquivo não exista

        Returns:
            Lista de arquivos ordenados
        """
        if not list_of_files:
            return []
        
        if not isinstance(list_of_files[0], str) or not isinstance(list_of_files[0], Path):
            raise ValueError(f"Tipo de dados {type(list_of_files[0])} não compátivel")
        
        list_of_files = [Path(file) if isinstance(file, str) else file for file in list_of_files]

        for file in list_of_files:
            if not file.exists:
                raise FileExistsError(f"O arquivo {file.__str__} não existe")
        
        return _ORDER_OPERATIONS.get(order_by, _ORDER_OPERATIONS[OrderBy.NAME_ASC])(list_of_files)

    def _verify_existence(list_of_files: List[Path]) -> bool:
        """
        Verifica
        """

def get_supply_chain_level_by_supplier(supplier):
    """ Вычисление уровня участника, основываясь на цепочке поставщиков """
    level = 0
    while supplier:
        level += 1
        supplier = supplier.supplier
    return level

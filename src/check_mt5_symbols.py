"""
检查MT5可用品种
"""
import MetaTrader5 as mt5

def check_symbols():
    """检查MT5中可用的品种"""
    if not mt5.initialize():
        print(f"MT5初始化失败: {mt5.last_error()}")
        return
    
    print(f"MT5版本: {mt5.version()}")
    print("=" * 60)
    
    # 获取所有品种
    symbols = mt5.symbols_get()
    
    if not symbols:
        print("未找到任何品种")
        mt5.shutdown()
        return
    
    print(f"\n总共有 {len(symbols)} 个品种\n")
    
    # 按类别分组
    forex = []
    metals = []
    indices = []
    crypto = []
    others = []
    
    for symbol in symbols:
        name = symbol.name
        if any(x in name for x in ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'NZD']):
            if not any(x in name for x in ['XAU', 'XAG', 'GOLD', 'SILVER']):
                forex.append(name)
        elif any(x in name for x in ['XAU', 'XAG', 'GOLD', 'SILVER', 'XAUUSD', 'XAGUSD']):
            metals.append(name)
        elif any(x in name for x in ['US30', 'US500', 'NAS100', 'DAX', 'FTSE', 'SPX']):
            indices.append(name)
        elif any(x in name for x in ['BTC', 'ETH', 'CRYPTO']):
            crypto.append(name)
        else:
            others.append(name)
    
    # 显示分类
    if metals:
        print(f"【贵金属】 ({len(metals)} 个)")
        for s in metals[:10]:
            print(f"  {s}")
        if len(metals) > 10:
            print(f"  ... 还有 {len(metals)-10} 个")
        print()
    
    if forex:
        print(f"【外汇】 ({len(forex)} 个)")
        for s in forex[:15]:
            print(f"  {s}")
        if len(forex) > 15:
            print(f"  ... 还有 {len(forex)-15} 个")
        print()
    
    if indices:
        print(f"【指数】 ({len(indices)} 个)")
        for s in indices[:10]:
            print(f"  {s}")
        if len(indices) > 10:
            print(f"  ... 还有 {len(indices)-10} 个")
        print()
    
    if crypto:
        print(f"【加密货币】 ({len(crypto)} 个)")
        for s in crypto[:10]:
            print(f"  {s}")
        if len(crypto) > 10:
            print(f"  ... 还有 {len(crypto)-10} 个")
        print()
    
    if others:
        print(f"【其他】 ({len(others)} 个)")
        for s in others[:10]:
            print(f"  {s}")
        if len(others) > 10:
            print(f"  ... 还有 {len(others)-10} 个")
        print()
    
    # 搜索功能
    print("=" * 60)
    search = input("\n输入关键词搜索品种 (直接回车跳过): ").strip().upper()
    if search:
        matches = [s.name for s in symbols if search in s.name.upper()]
        if matches:
            print(f"\n找到 {len(matches)} 个匹配的品种:")
            for m in matches:
                print(f"  {m}")
        else:
            print(f"未找到包含 '{search}' 的品种")
    
    mt5.shutdown()
    print("\nMT5连接已关闭")

if __name__ == "__main__":
    check_symbols()

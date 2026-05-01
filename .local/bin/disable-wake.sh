#!/bin/bash
########################################################################################
# DISABLE WAKE SOURCES - MacBook A1278
# Desabilita LID0 (tampa) que acorda o sistema durante suspensão
########################################################################################

echo "=== Desabilitando Wake da Tampa (LID0) ==="

# Verificar se LID0 está habilitado
if grep -q "^LID0.*enabled" /proc/acpi/wakeup 2>/dev/null; then
    echo "LID0 está habilitado, desabilitando..."
    echo LID0 > /proc/acpi/wakeup
    echo "✓ LID0 desabilitado"
else
    echo "✓ LID0 já está desabilitado"
fi

echo ""
echo "Estado atual do LID0:"
grep LID0 /proc/acpi/wakeup

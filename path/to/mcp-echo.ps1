$ErrorActionPreference = "Stop"
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$protocolVersion = "2025-03-26"
$serverTools = @(
    @{
        name = "echo"
        description = "Return the supplied text unchanged."
        inputSchema = @{
            type = "object"
            properties = @{
                text = @{ type = "string"; description = "Text to echo." }
            }
            required = @("text")
            additionalProperties = $false
        }
    }
    @{
        name = "echo_uppercase"
        description = "Return the supplied text in uppercase."
        inputSchema = @{
            type = "object"
            properties = @{
                text = @{ type = "string"; description = "Text to convert." }
            }
            required = @("text")
            additionalProperties = $false
        }
    }
    @{
        name = "echo_lowercase"
        description = "Return the supplied text in lowercase."
        inputSchema = @{
            type = "object"
            properties = @{
                text = @{ type = "string"; description = "Text to convert." }
            }
            required = @("text")
            additionalProperties = $false
        }
    }
)

function Write-JsonRpcMessage {
    param([Parameter(Mandatory = $true)][object]$Message)

    $json = ConvertTo-Json -InputObject $Message -Depth 20 -Compress
    [Console]::Out.WriteLine($json)
    [Console]::Out.Flush()
}

function Write-JsonRpcError {
    param(
        [object]$Id,
        [int]$Code,
        [string]$Message
    )

    Write-JsonRpcMessage @{
        jsonrpc = "2.0"
        id = $Id
        error = @{ code = $Code; message = $Message }
    }
}

function Write-ToolResult {
    param(
        [object]$Id,
        [string]$Text,
        [bool]$IsError = $false
    )

    Write-JsonRpcMessage @{
        jsonrpc = "2.0"
        id = $Id
        result = @{
            content = @(@{ type = "text"; text = $Text })
            isError = $IsError
        }
    }
}

while ($null -ne ($line = [Console]::In.ReadLine())) {
    try {
        $request = ConvertFrom-Json -InputObject $line -ErrorAction Stop
    }
    catch {
        Write-JsonRpcError -Id $null -Code -32700 -Message "Parse error"
        continue
    }

    if ($null -eq $request -or $request.jsonrpc -ne "2.0") {
        Write-JsonRpcError -Id $null -Code -32600 -Message "Invalid Request"
        continue
    }

    $hasId = $null -ne $request.PSObject.Properties["id"]
    $requestId = $request.id
    $method = $request.method

    if (-not $hasId) {
        if ($method -in @("notifications/initialized", "notifications/cancelled")) {
            continue
        }
        continue
    }

    try {
        switch ($method) {
            "initialize" {
                $supportedVersions = @("2025-03-26", "2024-11-05")
                $requestedVersion = $request.params.protocolVersion
                if ($requestedVersion -in $supportedVersions) {
                    $negotiatedVersion = $requestedVersion
                }
                else {
                    $negotiatedVersion = $protocolVersion
                }

                Write-JsonRpcMessage @{
                    jsonrpc = "2.0"
                    id = $requestId
                    result = @{
                        protocolVersion = $negotiatedVersion
                        capabilities = @{ tools = @{ listChanged = $false } }
                        serverInfo = @{
                            name = "echo-windows"
                            version = "1.0.0"
                        }
                    }
                }
                continue
            }
            "ping" {
                Write-JsonRpcMessage @{
                    jsonrpc = "2.0"
                    id = $requestId
                    result = @{}
                }
                continue
            }
            "tools/list" {
                Write-JsonRpcMessage @{
                    jsonrpc = "2.0"
                    id = $requestId
                    result = @{ tools = $serverTools }
                }
                continue
            }
            "tools/call" {
                $toolName = $request.params.name
                $arguments = $request.params.arguments
                $textProperty = $null
                if ($null -ne $arguments) {
                    $textProperty = $arguments.PSObject.Properties["text"]
                }
                if ($null -eq $textProperty -or $textProperty.Value -isnot [string]) {
                    Write-ToolResult -Id $requestId -Text "The text argument must be a string." -IsError $true
                    continue
                }

                $text = $textProperty.Value
                switch ($toolName) {
                    "echo" {
                        $output = $text
                    }
                    "echo_uppercase" {
                        $output = $text.ToUpperInvariant()
                    }
                    "echo_lowercase" {
                        $output = $text.ToLowerInvariant()
                    }
                    default {
                        Write-ToolResult -Id $requestId -Text "Unknown tool: $toolName" -IsError $true
                        continue
                    }
                }

                Write-ToolResult -Id $requestId -Text $output
                continue
            }
            default {
                Write-JsonRpcError -Id $requestId -Code -32601 -Message "Method not found"
                continue
            }
        }
    }
    catch {
        Write-JsonRpcError -Id $requestId -Code -32603 -Message "Internal error"
    }
}

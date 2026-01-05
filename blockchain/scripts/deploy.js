const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("🚀 Deploying ProcurementAudit contract...");

  // Get deployer account
  const [deployer] = await hre.ethers.getSigners();
  console.log("📝 Deploying with account:", deployer.address);

  // Deploy contract
  const ProcurementAudit = await hre.ethers.getContractFactory(
    "ProcurementAudit"
  );
  const contract = await ProcurementAudit.deploy();
  await contract.waitForDeployment();

  const contractAddress = await contract.getAddress();
  console.log("✅ ProcurementAudit deployed to:", contractAddress);

  // Save contract address and ABI
  const contractData = {
    address: contractAddress,
    abi: JSON.parse(contract.interface.formatJson()),
  };

  // Create directories if they don't exist
  const backendAbiDir = path.join(__dirname, "../../backend/app/services");
  const frontendConfigDir = path.join(__dirname, "../../frontend/src");

  try {
    // Save to backend (create directory first)
    if (!fs.existsSync(backendAbiDir)) {
      fs.mkdirSync(backendAbiDir, { recursive: true });
    }
    const backendAbiPath = path.join(
      backendAbiDir,
      "ProcurementAudit_ABI.json"
    );
    fs.writeFileSync(backendAbiPath, JSON.stringify(contractData.abi, null, 2));
    console.log("💾 ABI saved to backend:", backendAbiPath);
  } catch (error) {
    console.log(
      "⚠️  Could not save to backend (container path issue):",
      error.message
    );
  }

  try {
    // Save to frontend (create directory first)
    if (!fs.existsSync(frontendConfigDir)) {
      fs.mkdirSync(frontendConfigDir, { recursive: true });
    }
    const frontendConfigPath = path.join(
      frontendConfigDir,
      "contract-config.json"
    );
    fs.writeFileSync(frontendConfigPath, JSON.stringify(contractData, null, 2));
    console.log("💾 Contract config saved to frontend:", frontendConfigPath);
  } catch (error) {
    console.log(
      "⚠️  Could not save to frontend (container path issue):",
      error.message
    );
  }

  // Also save to blockchain directory (always works)
  const localAbiPath = path.join(__dirname, "../ProcurementAudit_ABI.json");
  fs.writeFileSync(localAbiPath, JSON.stringify(contractData.abi, null, 2));
  console.log("💾 ABI saved locally:", localAbiPath);

  const localConfigPath = path.join(__dirname, "../contract-config.json");
  fs.writeFileSync(localConfigPath, JSON.stringify(contractData, null, 2));
  console.log("💾 Contract config saved locally:", localConfigPath);

  console.log("\n🎉 Deployment complete!");
  console.log("📋 Summary:");
  console.log("   Contract:", contractAddress);
  console.log("   Network: Hardhat Local");
  console.log("   Deployer:", deployer.address);
  console.log("\n📝 Next steps:");
  console.log("   1. Update .env with CONTRACT_ADDRESS:", contractAddress);
  console.log("   2. Copy ABI files manually if needed:");
  console.log(
    "      - Backend: backend/app/services/ProcurementAudit_ABI.json"
  );
  console.log("      - Frontend: frontend/src/contract-config.json");
  console.log("\n⚠️  IMPORTANT: Update CONTRACT_ADDRESS in .env file!");
  console.log("   CONTRACT_ADDRESS=" + contractAddress);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
